# DocuMind: PDF Intelligence System
DocuMind is an intelligent document processing engine designed to analyze, extract, and synthesize information from large-scale PDF datasets. By leveraging Large Language Models (LLMs), vector databases, and multi-step agentic workflows, DocuMind provides high-fidelity answers and insights from complex documentation.

🚀 Key Features
Vectorized Search: Leverages pgvector for efficient, high-dimensional similarity search.

Agentic Workflows: Utilizes LangGraph for multi-step reasoning, allowing the system to handle complex queries that require multiple processing stages.

Scalable Architecture: Designed to handle heavy document loads with a clean separation between data ingestion and query processing.

LLM-Powered Extraction: Automated extraction of structured data from unstructured PDF text.

🛠 Tech Stack
Language: Python 3.11

Frameworks: FastAPI, LangGraph

Database: PostgreSQL 15 (with pgvector extension)

AI/LLM: Ollama (Local model execution)

Development: VS Code, Git

📋 Prerequisites
Ensure you have the following installed on your machine:

Python 3.11

PostgreSQL 15

Node.js 18+

Git

Ollama (Ensure Ollama is running before starting the backend)

⚙️ Getting Started
1. Clone the Repository
Bash
git clone <your-repo-url>
cd DocuMind
2. Environment Setup
Create a virtual environment and install the required dependencies:

Bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
3. Database Configuration
Install and initialize PostgreSQL 15.

Enable the vector extension in your database:

SQL
CREATE EXTENSION IF NOT EXISTS vector;
Configure your connection string in your .env file.

4. Running the Application
Ensure your Ollama service is running, then start the backend:

Bash
# Run using Uvicorn
uvicorn main:app --reload
🏗 Project Architecture
Ingestion Pipeline: Handles PDF parsing, chunking, and embedding generation.

Vector Store: Stores embeddings in PostgreSQL using pgvector.

Reasoning Engine: LangGraph-based state machine that orchestrates retrieval, synthesis, and response generation.