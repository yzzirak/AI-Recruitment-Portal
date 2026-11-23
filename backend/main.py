from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import engine, get_db, Base
from auth import (hash_password, verify_password, create_access_token,
                  get_current_user, create_reset_token, verify_reset_token)
from email_utils import send_reset_email
import models
from job_routes         import router as job_router
from application_routes import router as app_router
from ai_screening       import router as ai_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HireFast — AI Resume Screening",
    description="AI-Based Resume Screening and Job Description Matching System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(job_router)
app.include_router(app_router)
app.include_router(ai_router)


class RegisterRequest(BaseModel):
    name:         str
    email:        str
    password:     str
    role:         str            
    company_name: Optional[str] = None   


class LoginRequest(BaseModel):
    email:    str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token:        str
    new_password: str

@app.post("/register", tags=["Auth"])
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if req.role not in ("HR", "Candidate"):
        raise HTTPException(status_code=400, detail="Role must be HR or Candidate")

    if req.role == "HR" and not (req.company_name or "").strip():
        raise HTTPException(status_code=400, detail="Company name is required for HR accounts")

    if db.query(models.User).filter(models.User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        name         = req.name.strip(),
        email        = req.email.strip(),
        password     = hash_password(req.password),
        role         = req.role,
        company_name = req.company_name.strip() if req.company_name else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message":      "Registration successful",
        "user_id":      user.id,
        "role":         user.role,
        "company_name": user.company_name
    }


@app.post("/login", tags=["Auth"])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    if not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({
        "user_id": user.id, "email": user.email, "role": user.role
    })
    return {
        "access_token": token,
        "token_type":   "bearer",
        "user_id":      user.id,
        "name":         user.name,
        "role":         user.role,
        "company_name": user.company_name
    }

@app.post("/forgot_password", tags=["Auth"])
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    token = create_reset_token(user)
    emailed = send_reset_email(user.email, token)

    if emailed:
        return {"message": "Reset code sent to your email", "demo_mode": False}

    # SMTP not configured -> demo mode (for college demo only)
    print(f"[DEMO] Reset code for {user.email}: {token}")
    return {
        "message":    "Email not configured — demo mode",
        "demo_mode":  True,
        "reset_token": token
    }


@app.post("/reset_password", tags=["Auth"])
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if len(req.new_password.encode()) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 characters)")

    user = verify_reset_token(req.token.strip(), db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    user.password = hash_password(req.new_password)
    db.commit()
    return {"message": "Password reset successful. Please sign in."}

@app.get("/me", tags=["Auth"])
def me(current_user: models.User = Depends(get_current_user)):
    return {
        "id":           current_user.id,
        "name":         current_user.name,
        "email":        current_user.email,
        "role":         current_user.role,
        "company_name": current_user.company_name
    }


@app.get("/", tags=["Health"])
def root():
    return {"message": "HireFast API running", "docs": "/docs"}