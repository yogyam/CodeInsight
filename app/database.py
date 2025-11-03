from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from datetime import datetime
from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserMemory(Base):
    __tablename__ = "user_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    repository_id = Column(String(255), nullable=False, index=True)
    memory_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON)
    embedding = Column(Vector(384))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CodeEmbedding(Base):
    __tablename__ = "code_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(String(255), nullable=False, index=True)
    file_path = Column(Text, nullable=False)
    code_chunk = Column(Text, nullable=False)
    embedding = Column(Vector(384))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class PRReview(Base):
    __tablename__ = "pr_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    pr_number = Column(Integer, nullable=False)
    repository_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False)
    review_content = Column(Text)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
