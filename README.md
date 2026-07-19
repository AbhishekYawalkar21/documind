# DocuMind: PDF Intelligence System

It uses LLMs, vector databases, and multi-step reasoning (LangGraph) to understand, extract, and answer questions about documents at scale.

DocuMind is an intelligent document processing engine designed to analyze, extract, and synthesize information from large-scale PDF datasets. By leveraging Large Language Models (LLMs), vector databases, and multi-step agentic workflows, DocuMind provides high-fidelity answers and insights from complex documentation.

---

## 🚀 Key Features

* **Vectorized Search:** Leverages pgvector for efficient, high-dimensional similarity search.
* **Agentic Workflows:** Utilizes LangGraph for multi-step reasoning, allowing the system to handle complex queries that require multiple processing stages.
* **Scalable Architecture:** Designed to handle heavy document loads with a clean separation between data ingestion and query processing.
* **LLM-Powered Extraction:** Automated extraction of structured data from unstructured PDF text.

---

## 🛠 Tech Stack

* **Languages:** Python, TypeScript
* **Frameworks/Libraries:** FastAPI, LangGraph, React
* **Database:** PostgreSQL (with pgvector extension)
* **AI/LLM:** Ollama (Local model execution)
* **Development:** VS Code, Git, Node.js

---

## 🏗 Project Architecture

* **Ingestion Pipeline:** Handles PDF parsing, chunking, and embedding generation.
* **Vector Store:** Stores embeddings in PostgreSQL using pgvector.
* **Reasoning Engine:** LangGraph-based state machine that orchestrates retrieval, synthesis, and response generation.

---

## 📋 Prerequisites

Before starting, install:
* **Python 3.11**
* **PostgreSQL 15**
* **Node.js 18+**
* **Git**
* **VS Code**
* **Ollama**

---

## ⚙️ Getting Started

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd DocuMind
```

### 2. Environment Setup (Backend)
Create a virtual environment and install the required dependencies:
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Configuration
Install and initialize PostgreSQL 15.

Enable the vector extension in your database:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
Configure your connection string in your `.env` file.

### 4. Frontend Setup
Install the necessary package dependencies for the user interface:
```bash
# From the root directory, navigate to your frontend folder (e.g., cd frontend)
npm install
```

### 5. Running the Application

**Start the Backend:**
Ensure your Ollama service is running, then start the backend server:
```bash
# Run using Uvicorn
uvicorn main:app --reload
```

**Start the Frontend:**
Open a separate terminal window, navigate to your frontend directory, and launch the development environment:
```bash
npm run dev
```

---

## 🔒 Copyright & Licensing

> [!NOTE]
> © 2026 Abhishek Yawalkar. All rights reserved.
>
> This repository is strictly a personal project created for skill-building and hands-on learning purposes. Viewing and forking the repository for personal review is permitted under GitHub's Terms of Service. However, no permission is granted to copy, modify, redistribute, or use this source code, in whole or in part, for any commercial or non-commercial projects.
