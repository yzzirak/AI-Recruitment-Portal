#  AI-Based Recruitment & Resume Screening System

An intelligent web-based recruitment platform that automates resume screening and matches candidates with job descriptions using **AI, NLP, and semantic similarity**.

---

##Key Features

*  Role-based authentication (HR & Candidate)
*  Resume upload (PDF/DOCX)
*  AI-powered resume parsing & preprocessing
*  Semantic matching using Sentence Transformers
*  Candidate ranking with similarity scores (0–100%)
*  HR dashboard for shortlist / reject decisions
*  Structured backend with scalable architecture

---

##  System Architecture

```
Frontend (Streamlit)
        ↓
FastAPI Backend (Auth, Jobs, Applications)
        ↓
NLP Pipeline (spaCy + Transformers)
        ↓
PostgreSQL (Users, Jobs, Applications, Scores)
```

---

##  Project Structure

```
hirefast/
├── backend/
│   ├── main.py                 # FastAPI entry + auth endpoints
│   ├── database.py             # PostgreSQL connection
│   ├── models.py               # ORM models
│   ├── auth.py                 # JWT authentication & security
│   ├── job_routes.py           # Job management APIs
│   ├── application_routes.py   # Application handling APIs
│   └── ai_screening.py         # AI screening pipeline
│
├── nlp/
│   ├── resume_parser.py        # Resume text extraction
│   ├── preprocessing.py        # NLP cleaning pipeline
│   └── similarity_model.py     # Embeddings + similarity scoring
│
├── uploads/resumes/            # Stored resumes
├── app.py                      # Streamlit frontend
├── schema.sql                  # Database schema
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️ Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2️ Setup PostgreSQL

```bash
psql -U postgres -c "CREATE DATABASE hirefast;"
psql -U postgres -d hirefast -f schema.sql
```

###  Configure Environment

```bash
export DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/hirefast"
```

---

##  Run the Application

### Backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

 API Docs: http://localhost:8000/docs

### Frontend (Streamlit)

```bash
streamlit run app.py --server.port 8501
```

 App: http://localhost:8501

---

##  AI Pipeline (How It Works)

1.  Candidate uploads resume
2.  Text extracted using `pdfplumber` / `python-docx`
3.  Preprocessing via spaCy (tokenization, stopword removal, lemmatization)
4.  Text converted into embeddings using `all-MiniLM-L6-v2`
5.  Cosine similarity computed against job description
6.  Candidates ranked from highest to lowest match

---

##  API Endpoints

| Method | Endpoint                    | Description         |
| ------ | --------------------------- | ------------------- |
| POST   | /register                   | Register user       |
| POST   | /login                      | Authenticate user   |
| POST   | /create_job                 | Create job (HR)     |
| GET    | /jobs                       | List jobs           |
| POST   | /apply_job                  | Apply with resume   |
| GET    | /my_applications            | Candidate dashboard |
| GET    | /job_applicants/{job_id}    | HR view applicants  |
| POST   | /run_screening/{job_id}     | Run AI ranking      |
| PUT    | /shortlist/{application_id} | Shortlist           |
| PUT    | /reject/{application_id}    | Reject              |

---

## Database Design

| Table        | Description                    |
| ------------ | ------------------------------ |
| users        | User accounts (HR / Candidate) |
| jobs         | Job postings                   |
| applications | Candidate applications         |
| match_scores | AI-generated similarity scores |

