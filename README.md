# TalentSphere — AI-Assisted Recruitment & Job Matching Platform

## 1. Project Description

**TalentSphere** is a Django-based recruitment and Applicant Tracking System (ATS) designed to connect **Candidates and Recruiters** through a structured recruitment platform.

Candidates can create professional profiles, upload resumes, browse jobs and apply for suitable opportunities. Recruiters can create job postings, manage applications, review candidates, track recruitment metrics and identify suitable candidates using the matching system.

The platform also includes **resume extraction, skill-based job matching, ATS-style candidate ranking, analytics, skill-gap analysis, security features and rate limiting**.

---

## 2. Current Project Features

### 👤 Authentication & Role Management

* Candidate and Recruiter registration
* Login and logout
* Role-based access control
* Custom Django User model
* Secure password handling
* JWT-based authentication
* 10-digit phone number validation

### 👨‍💼 Recruiter Features

* Recruiter profile management
* Create and manage job postings
* View job applications
* View candidate profiles
* Filter and prioritize candidates
* Update application status
* Recruiter analytics and metrics

### 👨‍🎓 Candidate Features

* Candidate profile management
* Add skills, education, experience and projects
* Upload resume
* Browse available jobs
* Apply for jobs
* Track application status
* View matching information
* Identify missing skills and skill gaps

### 📄 Resume Processing

* PDF resume upload
* DOCX resume upload
* Resume text extraction
* Resume information processing
* Skill extraction
* Experience extraction
* Project information extraction
* File validation and upload size restrictions

### 🎯 Job & Candidate Matching

TalentSphere uses an explainable matching system to compare candidate profiles with job requirements.

**Matching Score:**

* **Skill Match — 55%**
* **Experience Match — 25%**
* **Keyword Relevance — 20%**

The system provides matching information and helps recruiters identify candidates who are better suited for a particular job.

### 📊 ATS Candidate Ranking

* Candidate priority/ranking
* Skill-based ranking
* Experience-based ranking
* Application status filtering
* Minimum match-score filtering
* Helps recruiters shortlist suitable candidates

### 📈 Analytics & Metrics

* Total jobs posted
* Total applications
* Total candidates
* Candidate application statistics
* Recruiter-specific statistics
* Weekly activity visualization
* Dashboard charts using Chart.js

### 🔐 Security & Reliability

* JWT authentication
* Secure architecture
* Role-based authorization
* Information leakage prevention
* Rate limiting for multiple requests
* Protection against excessive requests
* Frontend error handling
* Invalid request/error blocking and proper error messages

### 🧠 Skill Gap Analysis

* Compare candidate skills with job-required skills
* Identify missing skills
* Highlight areas for improvement
* Provide learning-path recommendations for missing skills

### ⚡ Scalability

* Designed with a modular Django architecture
* Database operations handled through Django ORM
* Rate limiting for handling multiple requests
* Architecture prepared for scaling toward **1000+ users**

---

## 3. Timeline Overview

| Week       | Activities Planned                                        | Activities Completed                                                                           |
| ---------- | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Week 1** | Project setup, requirements and authentication            | Django project setup, Candidate/Recruiter roles, login and registration                        |
| **Week 2** | Profiles, dashboards and job management                   | Candidate/Recruiter profiles, dashboards, job posting and job browsing                         |
| **Week 3** | Application and recruitment workflow                      | Job applications, application tracking and application status management                       |
| **Week 4** | Resume processing and matching                            | PDF/DOCX resume extraction, skill and experience processing, job matching                      |
| **Week 5** | Candidate ranking and recruiter metrics                   | ATS-style candidate ranking, recruiter metrics and application statistics                      |
| **Week 6** | Candidate metrics, interview scheduling and notifications | Candidate metrics, interview scheduling and email notification modules                         |
| **Week 7** | AI recommendation, security and skill-gap analysis        | Recommendation, JWT, secure architecture, rate limiting, error handling and skill-gap analysis |
| **Week 8** | Testing, optimization and final integration               | Module integration, workflow testing, debugging and final documentation                        |

---

## 4. Milestone Overview

| Milestone                | Major Features                                                                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Milestone 1**          | Authentication, Candidate/Recruiter roles, profiles, dashboards, job posting, job browsing and applications                                 |
| **Milestone 2**          | Resume upload, PDF/DOCX extraction, skill extraction, experience processing, matching and candidate ranking                                 |
| **Milestone 3**          | Recruiter metrics, Candidate metrics, email notifications, interview scheduling and analytics dashboard                                     |
| **Milestone 4**          | AI recommendations, JWT, secure architecture, information leakage prevention, rate limiting, frontend error handling and skill-gap analysis |
| **Optional Enhancement** | System architecture prepared for handling 1000+ users                                                                                       |

---

## 5. Team Contributions

| Team Member             | Contribution                                                                                                           |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Kuldeep Singh Bhati** | Recruiter Metrics — total jobs posted, applications received, candidates interviewed and recruiter-specific statistics |
| **Alby Grace Aby**      | Candidate Metrics — candidate application statistics, application status tracking and candidate-specific metrics       |
| **Sravani**             | Email Notification — email configuration, application/interview notifications and notification triggers                |
| **Inndhu**              | Interview Scheduling — interview scheduling, date/time management and interview status                                 |
| **Venket**              | Analytics Dashboard — dashboard statistics, charts, graphs and recruitment analytics                                   |

---

## 6. Technology Stack

| Technology       | Purpose                                  |
| ---------------- | ---------------------------------------- |
| **Python**       | Core programming language                |
| **Django**       | Backend web framework                    |
| **SQLite**       | Database                                 |
| **HTML**         | Frontend structure                       |
| **CSS**          | UI styling                               |
| **JavaScript**   | Client-side functionality and validation |
| **Chart.js**     | Analytics visualization                  |
| **Django ORM**   | Database operations                      |
| **pypdf**        | PDF resume extraction                    |
| **python-docx**  | DOCX resume extraction                   |
| **JWT**          | Authentication                           |
| **NLTK / spaCy** | NLP and resume processing                |

---

## 7. System Workflow

```text
Candidate / Recruiter
        ↓
   Registration
        ↓
      Login
        ↓
 Role-Based Dashboard
        ↓
 ┌───────────────┬────────────────┐
 │   Candidate   │    Recruiter   │
 └───────────────┴────────────────┘
        ↓
 Profile / Job Management
        ↓
 Resume Processing
        ↓
 Skill & Experience Extraction
        ↓
 Job-Candidate Matching
        ↓
 ATS Candidate Ranking
        ↓
 Application / Interview
        ↓
 Analytics & Recommendations
```

---

## 8. Matching Methodology

TalentSphere uses an explainable scoring mechanism instead of relying only on a black-box recommendation.

```text
Overall Match Score
        =
Skill Match        → 55%
Experience Match   → 25%
Keyword Relevance  → 20%
```

The system identifies:

* Matching skills
* Missing skills
* Relevant experience
* Keyword relevance
* Overall match score
* Candidate suitability

This information can be used by recruiters for shortlisting and by candidates for identifying their skill gaps.

---

## 9. Security Features

The project includes multiple security and reliability mechanisms:

* JWT-based authentication
* Role-based authorization
* Secure password handling
* Information leakage prevention
* Input and file validation
* Rate limiting
* Multiple-request handling
* Frontend error handling
* Proper error messages
* Unauthorized-access prevention

The rate-limiting mechanism helps prevent excessive repeated requests and protects the application from request abuse.

---

## 10. Future Scope

Potential future improvements include:

* Advanced AI-based recommendations
* More sophisticated NLP-based resume analysis
* Personalized learning paths
* Advanced recruiter analytics
* Cloud deployment
* Redis-based caching
* Production-grade database such as PostgreSQL
* Horizontal scaling for larger user loads
* Improved recommendation models
* Automated interview workflows

---

## 11. Conclusion

TalentSphere provides an integrated recruitment platform that simplifies the hiring process for both Candidates and Recruiters.

By combining **Django, resume processing, NLP, job matching, ATS candidate ranking, analytics, JWT authentication, security mechanisms, rate limiting and skill-gap analysis**, the project provides a structured approach to recruitment while helping candidates understand and improve their suitability for available opportunities.
