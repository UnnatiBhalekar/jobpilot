-- JobPilot database schema (PostgreSQL)
-- Design notes:
--   * bullet_tags is a junction table for the many-to-many bullet<->tag relationship
--   * bullets uses two nullable FKs + a CHECK constraint instead of a polymorphic
--     association, so the database enforces "belongs to exactly one parent"
--   * resumes is versioned per user (one row per tailored version, plus the
--     original "master" version with is_master = true)

CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    location        VARCHAR(255),
    phone           VARCHAR(50),
    linkedin_url    VARCHAR(500),
    github_url      VARCHAR(500),
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE resumes (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_master       BOOLEAN NOT NULL DEFAULT false,
    summary         TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);

CREATE TABLE experiences (
    id              BIGSERIAL PRIMARY KEY,
    resume_id       BIGINT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    company         VARCHAR(255) NOT NULL,
    role            VARCHAR(255) NOT NULL,
    location        VARCHAR(255),
    start_date      DATE NOT NULL,
    end_date        DATE,
    display_order   INT NOT NULL DEFAULT 0
);

CREATE INDEX idx_experiences_resume_id ON experiences(resume_id);

CREATE TABLE projects (
    id              BIGSERIAL PRIMARY KEY,
    resume_id       BIGINT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    tech_stack      VARCHAR(500),
    display_order   INT NOT NULL DEFAULT 0
);

CREATE INDEX idx_projects_resume_id ON projects(resume_id);

CREATE TABLE bullets (
    id              BIGSERIAL PRIMARY KEY,
    experience_id   BIGINT REFERENCES experiences(id) ON DELETE CASCADE,
    project_id      BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    text            TEXT NOT NULL,
    display_order   INT NOT NULL DEFAULT 0,
    CONSTRAINT chk_bullet_single_parent CHECK (
        (experience_id IS NOT NULL AND project_id IS NULL) OR
        (experience_id IS NULL AND project_id IS NOT NULL)
    )
);

CREATE INDEX idx_bullets_experience_id ON bullets(experience_id);
CREATE INDEX idx_bullets_project_id ON bullets(project_id);

CREATE TABLE tags (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE bullet_tags (
    bullet_id       BIGINT NOT NULL REFERENCES bullets(id) ON DELETE CASCADE,
    tag_id          BIGINT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (bullet_id, tag_id)
);

CREATE INDEX idx_bullet_tags_tag_id ON bullet_tags(tag_id);

CREATE TABLE education (
    id              BIGSERIAL PRIMARY KEY,
    resume_id       BIGINT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    institution     VARCHAR(255) NOT NULL,
    degree          VARCHAR(255) NOT NULL,
    location        VARCHAR(255),
    end_date        DATE,
    grade           VARCHAR(100),
    display_order   INT NOT NULL DEFAULT 0
);

CREATE TABLE skills (
    id              BIGSERIAL PRIMARY KEY,
    resume_id       BIGINT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    category        VARCHAR(100) NOT NULL,
    skill_name      VARCHAR(255) NOT NULL
);

CREATE INDEX idx_skills_resume_id ON skills(resume_id);

CREATE TABLE applications (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company             VARCHAR(255) NOT NULL,
    role                VARCHAR(255) NOT NULL,
    job_description     TEXT NOT NULL,
    tailored_resume_id  BIGINT REFERENCES resumes(id),
    cover_letter_text   TEXT,
    status              VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    applied_at          TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT now(),
    updated_at          TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);

CREATE TABLE application_status_history (
    id              BIGSERIAL PRIMARY KEY,
    application_id  BIGINT NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    status          VARCHAR(50) NOT NULL,
    changed_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_status_history_application_id ON application_status_history(application_id);
