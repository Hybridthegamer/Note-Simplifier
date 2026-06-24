# NoteSimplifier — Intelligent Academic Note Simplification System

An AI-powered web application for simplifying academic notes, extracting key concepts, and generating multiple-choice quizzes for exam preparation. Built as a Final Year Project implementing the full system architecture specified in Chapters 1–3.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Requirements](#system-requirements)
3. [Tool Stack & Rationale](#tool-stack--rationale)
4. [Project Structure](#project-structure)
5. [Setup & Installation](#setup--installation)
   - [Local Development (Without Docker)](#local-development-without-docker)
   - [Docker (Recommended for Production)](#docker-recommended-for-production)
6. [Environment Variables](#environment-variables)
7. [API Reference](#api-reference)
8. [Algorithms Implemented](#algorithms-implemented)

---

## Project Overview

NoteSimplifier addresses the problem of information overload for students preparing for examinations. The system accepts academic documents (PDF, DOCX, TXT) and processes them through a multi-stage NLP pipeline to produce:

- **Simplified notes** at Basic, Intermediate, or Advanced complexity levels
- **Key concept cards** with AI-generated contextual definitions
- **Multiple-choice quizzes** (5–20 questions) with instant scoring and feedback
- **Exportable outputs** in PDF and DOCX formats for offline revision

The system implements the three core algorithms specified in Chapter 3:
- **Algorithm 3.1** — Hybrid TF-IDF + GPT-4 text simplification pipeline
- **Algorithm 3.2** — KeyBERT + YAKE keyword extraction
- **Algorithm 3.3** — GPT-4 MCQ generation with JSON schema validation

---

## System Requirements

### Minimum Hardware
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8 GB |
| Disk | 5 GB | 20 GB |
| Network | Broadband | Broadband |

> **Note:** The HuggingFace Transformers BART model (~1.6 GB) is downloaded on first run. Ensure adequate disk space and internet connectivity during initial startup.

### Software Prerequisites
| Tool | Version | Purpose |
|------|---------|---------|
| Python | ≥ 3.11 | Backend runtime |
| Node.js | ≥ 20 LTS | Frontend build |
| npm | ≥ 10 | Frontend package manager |
| Docker + Docker Compose | Latest stable | Containerised deployment |
| MongoDB Atlas | Cloud (free tier) | Database |
| OpenAI API Key | Active | GPT-4 simplification & quiz gen |

---

## Tool Stack & Rationale

### Backend — Python 3.11 + Flask

**Why Python?**  
Python is the dominant language in the NLP and machine learning ecosystem. All major NLP libraries (HuggingFace Transformers, NLTK, KeyBERT, YAKE, spaCy) have first-class Python support. Chapter 3 explicitly specifies a Python backend, and PEP 8 compliance is a stated non-functional requirement.

**Why Flask (over Django)?**  
Flask is a micro-framework ideal for RESTful API design. The system has a stateless REST API architecture (Chapter 3, Section 3.4), which Flask implements cleanly through blueprints without the overhead of Django's ORM, admin, and template engine (none of which are needed when MongoDB is the data store and React is the frontend).

### Frontend — React.js 18 + Bootstrap 5 + Vite

**Why React.js?**  
React is explicitly named in Chapter 3 (Section 3.4 and 3.5.3) as the presentation tier technology. React's component-based architecture enables the modular, reusable UI elements (quiz cards, concept cards, upload zones) and efficient state management via React Hooks as specified. Vite is chosen as the build tool over Create React App for significantly faster hot module replacement and build times.

**Why Bootstrap 5?**  
Bootstrap 5 is directly specified in Chapter 3 (Section 3.4) for responsive styling. It provides the responsive grid, WCAG 2.1-compliant components, and cross-device compatibility (320px to 4K) required by the non-functional requirements without adding JavaScript framework overhead.

### Database — MongoDB Atlas

**Why MongoDB over PostgreSQL/MySQL?**  
Chapter 3 (Section 3.6) provides a detailed justification: the variable, deeply nested structure of AI-generated academic content (summaries, quiz items, concept lists) fits naturally into BSON documents. A relational schema would impose rigidity penalties for these polymorphic structures. MongoDB's horizontal sharding supports the 500+ concurrent user scalability target, and its schema-less nature accelerates iterative Agile development across five sprints.

**Why MongoDB Atlas (cloud-hosted)?**  
Atlas provides fully managed infrastructure including automated backups, multi-region replication, and a free tier suitable for development. This eliminates operational overhead and directly supports the 99.5% availability target.

### AI/NLP — OpenAI GPT-4 + HuggingFace Transformers

**Why GPT-4?**  
GPT-4 is specified in Chapter 3 as the abstractive simplification and quiz generation engine. Its chain-of-thought reasoning produces fluent, contextually accurate simplified prose across all three complexity levels (Basic/Intermediate/Advanced) and generates well-structured MCQs in JSON format as specified in Algorithm 3.3. GPT-4's instruction-following capability is essential for enforcing the structured output schema.

**Why HuggingFace Transformers (BART-large-CNN)?**  
BART-large-CNN is named explicitly in Chapter 3 (Section 3.4) as the extractive ranking model. It is used in the pre-processing stage of Algorithm 3.1 before GPT-4 abstractive generation. This two-stage hybrid approach produces more coherent summaries than single-stage abstractive models alone when applied to domain-specific academic texts.

**Why KeyBERT + YAKE?**  
Both are specified in Chapter 3 (Algorithm 3.2). KeyBERT provides semantic relevance through sentence-BERT cosine similarity embeddings, capturing meaning. YAKE provides statistical co-occurrence analysis, catching domain-specific terms not well-represented in embeddings. The hybrid captures both dimensions of keyword importance as validated in academic literature.

### Document Parsing — PyMuPDF + python-docx

Both are explicitly specified in Chapter 3 (Section 3.5.2). PyMuPDF is the leading Python PDF library for text extraction, offering page-level control and handling of complex PDF layouts. python-docx is the standard for DOCX processing.

### Authentication — Flask-JWT-Extended

JWT-based authentication is specified in Chapter 3 (Sections 3.3.2 and 3.3.3) with a 24-hour token expiry and bcrypt password hashing. Flask-JWT-Extended provides a clean decorator-based implementation that integrates with Flask blueprints.

### Export — ReportLab + python-docx

ReportLab generates professional PDF exports with custom styling. python-docx generates DOCX exports. Both satisfy the PDF/DOCX export functional requirement (Chapter 3, Section 3.3.2).

### Containerisation — Docker + Docker Compose

Chapter 3 (Section 3.3.3) states: "The system shall be containerised using Docker to facilitate deployment on any major cloud platform (AWS, Azure, Google Cloud) or on-premises server without modification of the source code." Docker Compose orchestrates the multi-service architecture (Flask backend, React/nginx frontend) locally.

---

## Project Structure

```
Note-Simplifier/
├── backend/                      # Flask REST API
│   ├── app/
│   │   ├── __init__.py           # Application factory, DB init
│   │   ├── models/               # MongoDB document models
│   │   │   ├── user.py           # Users collection (bcrypt, JWT)
│   │   │   ├── document.py       # Documents collection
│   │   │   ├── summary.py        # Summaries collection
│   │   │   └── quiz.py           # Quizzes collection
│   │   ├── routes/               # REST API endpoints
│   │   │   ├── auth.py           # /api/auth/* (register, login, me)
│   │   │   ├── documents.py      # /api/documents/* (upload, list, delete)
│   │   │   ├── processing.py     # /api/process/* (NLP pipeline)
│   │   │   ├── quiz.py           # /api/quiz/* (generate, submit)
│   │   │   ├── export.py         # /api/export/* (PDF/DOCX download)
│   │   │   └── admin.py          # /api/admin/* (stats, user management)
│   │   ├── services/             # Core business logic
│   │   │   ├── text_extractor.py # PDF/DOCX/TXT extraction (PyMuPDF)
│   │   │   ├── nlp_pipeline.py   # Algorithm 3.1 (TF-IDF + GPT-4)
│   │   │   ├── keyword_extractor.py # Algorithm 3.2 (KeyBERT + YAKE)
│   │   │   ├── quiz_generator.py # Algorithm 3.3 (GPT-4 MCQ)
│   │   │   └── export_service.py # PDF/DOCX generation (ReportLab)
│   │   └── middleware/
│   │       └── auth_middleware.py # JWT decorators (require_auth, require_admin)
│   ├── requirements.txt
│   ├── run.py                    # Entry point
│   ├── Dockerfile
│   └── .env.example
├── frontend/                     # React.js SPA
│   ├── src/
│   │   ├── App.jsx               # Routes + protected route guards
│   │   ├── main.jsx              # React DOM render
│   │   ├── index.css             # Global styles + CSS variables
│   │   ├── context/
│   │   │   └── AuthContext.jsx   # JWT auth state + login/logout
│   │   ├── services/
│   │   │   └── api.js            # Axios with JWT interceptors
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx     # /login
│   │   │   ├── RegisterPage.jsx  # /register
│   │   │   ├── DashboardPage.jsx # /dashboard (stats + recent docs)
│   │   │   ├── UploadPage.jsx    # /upload (dropzone + config)
│   │   │   ├── ResultsPage.jsx   # /results/:summaryId (notes + concepts)
│   │   │   ├── QuizPage.jsx      # /quiz/:quizId (interactive quiz)
│   │   │   ├── HistoryPage.jsx   # /history (all sessions)
│   │   │   └── AdminPage.jsx     # /admin (user & system management)
│   │   └── components/
│   │       └── common/
│   │           └── Layout.jsx    # Sidebar navigation layout
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Setup & Installation

### Local Development (Without Docker)

#### 1. Clone the repository

```bash
git clone https://github.com/hybridthegamer/note-simplifier.git
cd note-simplifier
```

#### 2. Backend setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data (first run only)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI and OpenAI API key

# Start the Flask server
python run.py
# API available at http://localhost:5000
```

#### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Set VITE_API_URL=http://localhost:5000/api

# Start the development server
npm run dev
# App available at http://localhost:3000
```

---

### Docker (Recommended for Production)

#### 1. Create the environment file

```bash
cp backend/.env.example .env
# Fill in all required values
```

#### 2. Build and start all services

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

#### 3. Stop services

```bash
docker-compose down
```

---

## Environment Variables

Create a `.env` file in the `backend/` directory (for local dev):

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | No | `development` or `production` (default: production) |
| `SECRET_KEY` | **Yes** | Flask session secret — use a long random string |
| `JWT_SECRET_KEY` | **Yes** | JWT signing secret — use a long random string |
| `JWT_ACCESS_TOKEN_EXPIRES` | No | Token lifetime in seconds (default: 86400 = 24h) |
| `MONGO_URI` | **Yes** | MongoDB Atlas connection string (includes database name) |
| `OPENAI_API_KEY` | **Yes** | OpenAI API key with GPT-4 access |
| `MAX_CONTENT_LENGTH` | No | Max upload size in bytes (default: 20971520 = 20 MB) |
| `UPLOAD_FOLDER` | No | Server-side temp upload directory (default: `uploads`) |
| `FRONTEND_URL` | No | CORS origin for the React app (default: `http://localhost:3000`) |

### Getting a MongoDB URI

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a database user with read/write privileges
3. Whitelist your IP (or use `0.0.0.0/0` for development)
4. Click **Connect → Connect your application** and copy the URI
5. Replace `<username>`, `<password>`, and append `/academic_notes_db` as the database name

### Getting an OpenAI API Key

1. Create an account at [platform.openai.com](https://platform.openai.com)
2. Navigate to **API Keys** and create a new key
3. Ensure your account has GPT-4 API access (may require payment method)

> **Cost estimate:** Processing a 5,000-word document costs approximately $0.05–$0.15 with GPT-4 depending on output length.

---

## API Reference

All endpoints are prefixed with `/api`.

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | None | Create new account |
| POST | `/auth/login` | None | Login and receive JWT |
| GET | `/auth/me` | JWT | Get current user profile |

### Documents

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/documents/upload` | JWT | Upload PDF/DOCX/TXT (multipart) |
| GET | `/documents/` | JWT | List user's documents |
| GET | `/documents/:id` | JWT | Get document metadata |
| DELETE | `/documents/:id` | JWT | Delete document and summaries |

### Processing (NLP Pipeline)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/process/:docId` | JWT | Run full NLP pipeline on document |
| GET | `/process/:docId/summaries` | JWT | List summaries for a document |
| GET | `/process/summary/:summaryId` | JWT | Get summary + concepts |

### Quiz

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/quiz/generate/:summaryId` | JWT | Generate MCQ quiz from summary |
| GET | `/quiz/:quizId` | JWT | Get quiz (without answers) |
| POST | `/quiz/:quizId/submit` | JWT | Submit answers and get score |
| GET | `/quiz/summary/:summaryId` | JWT | List quizzes for a summary |

### Export

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/export/notes/:summaryId/pdf` | JWT | Download simplified notes as PDF |
| GET | `/export/notes/:summaryId/docx` | JWT | Download simplified notes as DOCX |
| GET | `/export/quiz/:quizId/pdf` | JWT | Download quiz with answers as PDF |
| GET | `/export/quiz/:quizId/docx` | JWT | Download quiz with answers as DOCX |

### Admin (Admin role required)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/stats` | Admin | System usage statistics |
| GET | `/admin/users` | Admin | List all registered users |
| DELETE | `/admin/users/:id` | Admin | Delete a user account |

---

## Algorithms Implemented

### Algorithm 3.1 — Text Simplification (`backend/app/services/nlp_pipeline.py`)

Two-stage hybrid pipeline:
1. **Preprocessing:** Sentence tokenisation (NLTK Punkt), TF-IDF scoring, extraction of top 40% key sentences
2. **Chunk Management:** Sentences split into ≤1024 token chunks
3. **Abstractive Simplification:** Each chunk sent to GPT-4 with a complexity-level-specific system prompt
4. **Post-processing:** Chunks rejoined and reformatted

### Algorithm 3.2 — Keyword Extraction (`backend/app/services/keyword_extractor.py`)

Hybrid two-method approach:
1. **KeyBERT:** Sentence-BERT embeddings → cosine similarity ranking of n-gram candidates
2. **YAKE:** Statistical co-occurrence analysis for domain-specific term coverage
3. **Merge + Deduplicate:** Union by lemma, ranked by combined score
4. **Definition Enrichment:** GPT-4 generates one-sentence in-context definitions

### Algorithm 3.3 — Quiz Generation (`backend/app/services/quiz_generator.py`)

GPT-4 guided MCQ generation:
1. **Prompt Construction:** Structured prompt specifying JSON output schema
2. **GPT-4 Call:** `response_format: json_object` ensures valid JSON
3. **Schema Validation:** Each question validated for required keys and option count
4. **Option Shuffling:** Options randomly reordered with correct index updated to match

---

*Built as part of a Final Year Project: "An Intelligent Web-Based System for Simplifying Academic Notes and Textbooks for Examination Preparation"*