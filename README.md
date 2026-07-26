# DocuMind: PDF Intelligence System

DocuMind is an intelligent document processing engine that uses **local Ollama LLMs** (completely free — no API costs) to analyze, extract, and synthesize information from large-scale PDF datasets. By leveraging Large Language Models, vector databases, and a multi-step LangGraph agent, DocuMind provides high-fidelity answers and insights from complex documentation.

---

## 🚀 Key Features

* 📄 **PDF Upload** — drag-and-drop interface for document ingestion
* 🤖 **Local AI Analysis** — powered by Ollama, no API costs, no rate limits
* 👥 **Entity Extraction** — names, dates, amounts, emails, and more
* ⚠️ **Compliance Checking** — flags GDPR, PII, and security issues
* 🔗 **Knowledge Graph Creation** — maps relationships between entities
* 💬 **Real-Time Q&A** — ask questions directly against a document
* 📚 **Document History Tracking** — persistent analysis records
* 🔍 **Vectorized Search** — pgvector-powered semantic similarity search
* 🧠 **Agentic Workflows** — LangGraph multi-step reasoning for complex queries
* 📈 **Scalable Architecture** — clean separation between ingestion and query processing

---

## 🏗 Architecture

* **Backend:** FastAPI + PostgreSQL + Ollama
* **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
* **AI:** LangGraph multi-step agent running on local Ollama models
* **Deployment:** Docker + Docker Compose

---

## 🛠 Tech Stack

### Backend
* FastAPI 0.104+ (REST API)
* PostgreSQL 15 + pgvector (database)
* SQLAlchemy 2.0 (ORM)
* Ollama (local LLM)
* LangGraph (multi-step agent)
* PyPDF + pdfplumber (text extraction)

### Frontend
* React 18 + TypeScript
* Vite (build tool and dev server)
* Tailwind CSS (styling)
* Axios (HTTP client)
* Zustand (state management)

### Infrastructure
* Docker + Docker Compose
* Nginx (reverse proxy and static file serving in production)
* PostgreSQL with pgvector extension
* Ollama service
* GitHub Actions (CI/CD)

---

## 🔄 How It Works

```
PDF Upload
   ↓
Text Extraction (pypdf + pdfplumber)
   ↓
Semantic Chunking (with overlap)
   ↓
LangGraph 5-Node Agent Analysis:
   ├─ Node 1: Summarization
   ├─ Node 2: Entity Extraction
   ├─ Node 3: Compliance Checking
   ├─ Node 4: Relationship Mapping
   └─ Node 5: Q&A Preparation
   ↓
Store Results in PostgreSQL + pgvector
   ↓
Display Results in Frontend
```

Each node in the LangGraph agent is independent, which keeps the pipeline modular, testable, and easy to extend with new analysis capabilities.

---

## ⚙️ Getting Started

```bash
git clone <this-repo-url>
cd documind
```

**Option A — Docker (recommended, fastest)**

Requires only Docker Desktop — no local Python, Node.js, or PostgreSQL install needed. Postgres and Ollama both run as containers, and the backend/frontend are built and run inside containers too.

```bash
docker-compose build
docker-compose up -d
```
On the first run, the Ollama container downloads its model (~4GB), so the backend may take a few extra minutes to become available.

**Option B — Manual setup**

Requires Python 3.11+, Node.js 18+, PostgreSQL 15 with the `pgvector` extension enabled, and [Ollama](https://ollama.ai) installed and running locally with a pulled model (e.g. `ollama pull mistral`).

Backend:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env       # then fill in your values
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## 🌍 Real-World Applications

* Legal document analysis
* Contract review automation
* Compliance checking
* Financial document processing
* HR document screening
* Customer document processing

---

## 🔒 Copyright & Licensing

> [!NOTE]
> © 2026 Abhishek Yawalkar. All rights reserved.
>
> This repository is a personal project created for skill-building and hands-on learning purposes. Viewing and forking the repository for personal review is permitted under GitHub's Terms of Service. However, no permission is granted to copy, modify, redistribute, or use this source code, in whole or in part, for any commercial or non-commercial projects.
>
> For inquiries regarding usage or collaboration, please contact the copyright holder directly.