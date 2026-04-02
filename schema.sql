CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL,
    role       VARCHAR(20)  NOT NULL CHECK (role IN ('HR','Candidate')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id               SERIAL PRIMARY KEY,
    title                VARCHAR(200) NOT NULL,
    description          TEXT         NOT NULL,
    sector               VARCHAR(100) NOT NULL,
    education_required   VARCHAR(100) NOT NULL,
    skills_required      TEXT         NOT NULL,
    experience_required  VARCHAR(50)  NOT NULL,
    posted_by            INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at           TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS applications (
    id           SERIAL PRIMARY KEY,
    candidate_id INTEGER     NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
    job_id       INTEGER     NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    resume_path  VARCHAR(500) NOT NULL,
    status       VARCHAR(50)  DEFAULT 'applied'
                 CHECK (status IN ('applied','shortlisted','rejected')),
    applied_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (candidate_id, job_id)
);

CREATE TABLE IF NOT EXISTS match_scores (
    id           SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
    job_id       INTEGER NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    score        FLOAT   NOT NULL,
    screened_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (candidate_id, job_id)
);

CREATE INDEX IF NOT EXISTS idx_users_email     ON users(email);
CREATE INDEX IF NOT EXISTS idx_jobs_sector     ON jobs(sector);
CREATE INDEX IF NOT EXISTS idx_apps_job        ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_apps_candidate  ON applications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_scores_job      ON match_scores(job_id);
