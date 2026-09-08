# TalentSphere Elevate — Django Backend

A full-stack rebuild of the auth frontend: Django + MySQL, with role-based
signup/login (Candidate / Recruiter), dashboards, complete profile
management, job posting, and job applications.

## What changed from the static version

- **Phone validation fixed**: was accepting 7–12 digits, now strictly **10 digits**
  (enforced in both the JS on the page *and* server-side in `accounts/forms.py`
  and the `CustomUser.phone` model field — so it can never be bypassed).
- **Real database**: SQLite, via Django's ORM — a single file (`db.sqlite3`), no server or setup required.
- **Dashboards**:
  - Recruiter → jobs posted, current job, total applicants, list of postings.
  - Candidate → jobs applied, shortlisted count, open job openings, application list.
- **Profile management**:
  - Recruiter → name, email, company, designation, website, industry, size, location, about.
  - Candidate → name, email, DOB, location, education, experience (years),
    current company/designation, skills, projects, professional summary,
    expected salary, notice period, LinkedIn/GitHub/portfolio links, and a
    **resume upload**.
- **Jobs**: recruiters post jobs; candidates browse and apply with one click;
  recruiters see every applicant per job and can move them through
  Applied → Shortlisted → Selected/Rejected.
- **Candidates directory**: recruiters can browse *every* registered candidate
  (not just applicants) and open their full profile.

## Project layout

```
backend/
  manage.py
  config/            # settings, urls, wsgi/asgi
  accounts/          # CustomUser, RecruiterProfile, CandidateProfile, auth views
  jobs/               # Job, Application, post/browse/apply views
  templates/          # all HTML (extends the original brass/indigo design)
  static/css/styles.css   # original design tokens, reused as-is
  static/css/app.css      # new styles for dashboard/profile/job pages
  static/js/auth.js       # updated validation (10-digit phone) + real form submit
  media/              # uploaded resumes land here
  requirements.txt
```

## 1. Install prerequisites

You need **Python 3.10+**. That's it — no database server to install or configure.

```powershell
# from inside the backend/ folder
python -m venv venv
venv\Scripts\activate          # on Windows
# source venv/bin/activate     # on macOS/Linux

pip install -r requirements.txt
```

## 2. Migrate & run

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Open **http://127.0.0.1:8000/signup/** to create an account, or
**http://127.0.0.1:8000/login/** to sign in. Django admin is at
**http://127.0.0.1:8000/admin/**.

## How the roles work

- On signup, choose **"I'm a Candidate"** or **"I'm a Recruiter"** — this sets
  `role` on the user and creates a matching empty profile automatically.
  You're redirected straight to **Profile** to fill it in.
- Login is the same form for both roles; after signing in you're routed to
  the right dashboard automatically based on your stored role.
- Recruiters get **Post a Job**, **My Jobs**, **Candidates** in the nav.
- Candidates get **Browse Jobs** in the nav.

## Notes

- **Switching to a real server database later** (MySQL, PostgreSQL,
  Oracle, etc.): just change the `DATABASES` dict in `config/settings.py`
  to that engine's backend, install its driver, and re-run
  `python manage.py migrate` — the rest of the app (models, views,
  templates) doesn't need to change at all.
- `DEBUG = True` and `SECRET_KEY` are development defaults — change both
  before deploying anywhere public.
- Resumes are stored under `media/resumes/` and served locally in DEBUG mode.
- The math captcha and "slide to verify" on signup/login are front-end UX
  gates (kept from the original design); real validation and security
  (password hashing, CSRF, uniqueness checks) all happen server-side in
  Django.

## Job Matching — integrated Milestone 2

The Milestone 2 matching logic is integrated into this same Django project.
It reuses the existing `accounts.CandidateProfile` and `jobs.Job` models, so
there is only one Django project, one database, and one server.

- Candidate navigation: **Job Matches**
- URL: `/matching/`
- Matching logic: `matching/services.py`
- Candidate skills are read from the existing comma-separated profile field.
- Job skills are read from the existing comma-separated `skills_required` field.
- Applications use the existing `jobs.Application` model.

Run:

```powershell
python manage.py migrate
python manage.py runserver
```

### Important for the integrated ZIP

This package includes the `accounts` and `jobs` initial migration files.
Because the supplied `db.sqlite3` already contains those tables and records
the initial migrations as applied, **do not delete `db.sqlite3`**.

From the folder containing `manage.py` run:

```powershell
python manage.py migrate
python manage.py runserver
```

If Django reports that an initial table already exists because you are using a
different database, use:

```powershell
python manage.py migrate --fake-initial
```

### Resume handling

Candidate profiles support a connected resume upload using the existing
`CandidateProfile.resume` field. Upload validation accepts only **PDF or DOCX**
files and limits uploads to **5 MB**. The uploaded file is stored under
`media/resumes/` and is linked directly from the candidate profile. In
development mode, Django serves the uploaded resume from the media URL.


## Skill Gap Analysis — Milestone 3 / 1,000-user scalability

The project now includes a candidate-facing skill-gap workflow built on the existing
Django `jobs`, `accounts`, and `matching` apps.

### Where the data lives

- **Job description:** `jobs.Job.description`
- **Job responsibilities:** `jobs.Job.responsibilities`
- **Recruiter-entered skills:** `jobs.Job.skills_required`
- **Normalized/cached job skills:** `jobs.Job.parsed_skills`
- **Candidate skills:** `accounts.CandidateProfile.skills`
- **Normalized/cached candidate skills:** `accounts.CandidateProfile.parsed_skills`
- **Candidate resume:** `accounts.CandidateProfile.resume`

### Skill-gap flow

Job skills are extracted and normalized when a job is saved. Candidate skills are
normalized when the candidate profile is saved or resume extraction updates the
profile. Candidate requests then compare the cached canonical skill lists instead
of repeatedly parsing the full job description/resume.

For example:

```text
Job:       Python, Java, R, PHP, React, AI, Kubernetes, Docker
Candidate: Python, Java, React

Match:     37.5%
Missing:   R, PHP, AI, Kubernetes, Docker
```

Common aliases are normalized, including `K8s -> Kubernetes`, `React.js -> React`,
`JS -> JavaScript`, and `Kubernates -> Kubernetes`.

### Candidate endpoints

- HTML skill-gap page: `/jobs/<job_id>/skill-gap/`
- JSON API: `/jobs/<job_id>/skill-gap/api/`

Both endpoints are protected so a candidate can only inspect their own skill gap
for an active job.

### Existing Apply flow

`jobs.views.apply_job_view` remains the application entry point. The application
is saved using the existing `jobs.Application` model, then the candidate is sent
to the skill-gap page. The apply page also shows a skill-gap preview before the
candidate submits the application.

### Scalability

The implementation avoids an AI/NLP call on every candidate page view:

1. Parse a job once when it is created/updated.
2. Store canonical job skills in `Job.parsed_skills`.
3. Store canonical candidate skills in `CandidateProfile.parsed_skills`.
4. Compare the two small normalized lists using set operations.
5. Cache repeated skill-gap responses for five minutes.
6. Use database indexes on job/application access paths.

For local development the cache uses Django's in-process `LocMemCache`. For a
multi-worker production deployment, set `REDIS_URL` and the project automatically
uses Django's Redis cache backend.

PostgreSQL is recommended for production concurrency. SQLite remains the default
for local development.

### Database migrations

Run:

```powershell
python manage.py migrate
```

New migrations:

- `accounts/0007_candidate_skill_cache.py`
- `jobs/0007_skill_gap_indexes.py`

The candidate migration backfills `parsed_skills` from existing profile skills.
The job skill cache was already introduced by `jobs/0006_skill_gap_scalability.py`.

### Background processing

A separate task queue is not required for the current 1,000-user target because
skill extraction uses the project's lightweight local skill catalog. Resume parsing
only happens when a resume is uploaded/changed. If resume volume or parsing time
grows substantially, the resume extraction step can be moved to Celery/RQ with
Redis without changing the candidate-facing API.
#   T A L E N T - S P H E R E - E L E V A T E  
 