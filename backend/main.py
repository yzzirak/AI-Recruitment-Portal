from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import engine, get_db, Base
from auth import hash_password, verify_password, create_access_token, get_current_user
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