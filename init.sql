-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- User memory table
CREATE TABLE IF NOT EXISTS user_memory (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    repository_id VARCHAR(255) NOT NULL,
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Code embeddings table
CREATE TABLE IF NOT EXISTS code_embeddings (
    id SERIAL PRIMARY KEY,
    repository_id VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    code_chunk TEXT NOT NULL,
    embedding vector(384),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PR review history table
CREATE TABLE IF NOT EXISTS pr_reviews (
    id SERIAL PRIMARY KEY,
    pr_number INTEGER NOT NULL,
    repository_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    review_content TEXT,
    comments_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_memory_user_repo ON user_memory(user_id, repository_id);
CREATE INDEX IF NOT EXISTS idx_code_embeddings_repo ON code_embeddings(repository_id);
CREATE INDEX IF NOT EXISTS idx_pr_reviews_repo_pr ON pr_reviews(repository_id, pr_number);

-- Create vector similarity search indexes
CREATE INDEX IF NOT EXISTS idx_user_memory_embedding ON user_memory USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_code_embeddings_embedding ON code_embeddings USING ivfflat (embedding vector_cosine_ops);
