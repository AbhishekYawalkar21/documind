-- Create extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  filename VARCHAR(255) NOT NULL,
  file_content BYTEA NOT NULL,
  file_size_bytes INT NOT NULL,
  mime_type VARCHAR(100) DEFAULT 'application/pdf',
  pdf_metadata JSONB DEFAULT '{}',
  status VARCHAR(50) DEFAULT 'uploaded',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks
CREATE TABLE IF NOT EXISTS document_chunks (
  id SERIAL PRIMARY KEY,
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INT NOT NULL,
  content TEXT NOT NULL,
  start_position INT,
  end_position INT,
  page_number INT,
  embedding vector(1536),
  token_count INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results
CREATE TABLE IF NOT EXISTS analysis_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  summary TEXT,
  topics TEXT[] DEFAULT '{}',
  entities JSONB DEFAULT '{}',
  compliance_flags JSONB DEFAULT '{}',
  knowledge_graph JSONB DEFAULT '{}',
  raw_analysis JSONB,
  analysis_status VARCHAR(50) DEFAULT 'pending',
  analysis_started_at TIMESTAMP,
  analysis_completed_at TIMESTAMP,
  processing_time_seconds FLOAT
);

-- Q&A History
CREATE TABLE IF NOT EXISTS qa_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  user_query TEXT NOT NULL,
  ai_response TEXT NOT NULL,
  relevant_chunks INT[] DEFAULT '{}',
  confidence_score FLOAT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_analysis_document_id ON analysis_results(document_id);
CREATE INDEX idx_qa_history_document_id ON qa_history(document_id);
CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);