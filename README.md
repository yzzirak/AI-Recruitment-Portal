# 🚀 HireFast — AI-Based Resume Screening System

**Minor Project | B.Tech CSE | ITM University**
Submitted to: Dr. Manali Shukla
Supervisor: Ms. Harshita Chaurasiya
Team: Shreya Savita · Muskan Gupta · Priya Sarkar

---

## Project Overview

An intelligent web-based recruitment system that automatically screens
candidate resumes and matches them with job descriptions using AI and NLP,
exactly as described in the project synopsis.

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | Streamlit (unified app)             |
| Backend     | FastAPI                             |
| Database    | PostgreSQL + SQLAlchemy ORM         |
| Auth        | JWT (python-jose + bcrypt)          |
| NLP         | spaCy (en_core_web_sm)              |
| AI Model    | Sentence Transformers all-MiniLM-L6-v2 |
| Similarity  | Cosine Similarity (scikit-learn)    |
| Resume Parse| pdfplumber (PDF) + python-docx (DOCX) |

---

## Folder Structure

```
hirefast/
├── backend/
│   ├── main.py                 # FastAPI entry + auth endpoints
│   ├── database.py             # PostgreSQL connection
│   ├── models.py               # ORM: users, jobs, applications, match_scores
│   ├── auth.py                 # JWT tokens, password hashing, role guards
│   ├── job_routes.py           # Job CRUD + filter + shortlist/reject
│   ├── application_routes.py   # Apply (resume upload) + view applicants
│   └── ai_screening.py         # /run_screening — full AI pipeline
├── nlp/
│   ├── resume_parser.py        # pdfplumber + python-docx text extraction
│   ├── preprocessing.py        # spaCy NLP pipeline
│   └── similarity_model.py     # Sentence Transformers + cosine similarity
├── uploads/resumes/            # Uploaded resume files stored here
├── app.py                      # Unified Streamlit frontend
├── schema.sql                  # PostgreSQL DDL
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Set up PostgreSQL
```bash
psql -U postgres -c "CREATE DATABASE hirefast;"
psql -U postgres -d hirefast -f schema.sql
```

### 3. Configure DB URL
Edit `backend/database.py` or set environment variable:
```bash
export DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/hirefast"
```

### 4. Start FastAPI backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### 5. Start Streamlit frontend
```bash
streamlit run app.py --server.port 8501
```
App: http://localhost:8501

---

## AI Pipeline (Synopsis Methodology)

```
1. Resume Collection   → Candidate uploads PDF/DOCX via apply form
2. Text Extraction     → pdfplumber (PDF) / python-docx (DOCX)
3. NLP Processing      → spaCy: lowercase → remove noise →
                         tokenise → remove stopwords → lemmatise
4. Semantic Matching   → Sentence Transformer (all-MiniLM-L6-v2)
                         converts text to 384-dim embeddings
5. Candidate Ranking   → Cosine similarity score (0–100%)
                         sorted highest → lowest
6. HR Interface        → Ranked list with scores, shortlist/reject buttons
```

---

## API Endpoints

| Method | Endpoint                    | Role      | Description              |
|--------|-----------------------------|-----------|--------------------------|
| POST   | /register                   | Any       | Register HR or Candidate |
| POST   | /login                      | Any       | Login, get JWT token     |
| POST   | /create_job                 | HR        | Post a new job           |
| GET    | /jobs                       | Any       | List all jobs            |
| POST   | /apply_job                  | Candidate | Apply + upload resume    |
| GET    | /my_applications            | Candidate | View own applications    |
| GET    | /job_applicants/{job_id}    | HR        | View applicants for job  |
| POST   | /run_screening/{job_id}     | HR        | Run AI screening         |
| GET    | /filter_candidates          | HR        | Filter by edu/sector/skill|
| PUT    | /shortlist/{application_id} | HR        | Shortlist candidate      |
| PUT    | /reject/{application_id}    | HR        | Reject candidate         |

---

## Database Schema

| Table        | Key Columns                                      |
|--------------|--------------------------------------------------|
| users        | id, name, email, password (bcrypt), role         |
| jobs         | job_id, title, description, sector, skills       |
| applications | id, candidate_id, job_id, resume_path, status    |
| match_scores | id, candidate_id, job_id, score (0–100)          |
