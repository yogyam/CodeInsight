from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.database import CodeEmbedding, UserMemory
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    def __init__(self):
        # Using a lightweight model for embeddings (384 dimensions)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
    
    def create_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {e}")
            raise
    
    async def store_code_embedding(
        self,
        db: Session,
        repository_id: str,
        file_path: str,
        code_chunk: str,
        metadata: Optional[dict] = None
    ):
        """Store code chunk with its embedding."""
        embedding = self.create_embedding(code_chunk)
        
        code_emb = CodeEmbedding(
            repository_id=repository_id,
            file_path=file_path,
            code_chunk=code_chunk,
            embedding=embedding,
            metadata=metadata or {}
        )
        
        db.add(code_emb)
        db.commit()
        
        return code_emb
    
    async def search_similar_code(
        self,
        db: Session,
        repository_id: str,
        query: str,
        limit: int = 5
    ) -> List[CodeEmbedding]:
        """Search for similar code chunks using vector similarity."""
        query_embedding = self.create_embedding(query)
        
        # PostgreSQL pgvector similarity search
        results = db.query(CodeEmbedding).filter(
            CodeEmbedding.repository_id == repository_id
        ).order_by(
            CodeEmbedding.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()
        
        return results
    
    async def search_user_memory(
        self,
        db: Session,
        user_id: str,
        repository_id: str,
        query: str,
        limit: int = 3
    ) -> List[UserMemory]:
        """Search user memory for relevant context."""
        query_embedding = self.create_embedding(query)
        
        results = db.query(UserMemory).filter(
            UserMemory.user_id == user_id,
            UserMemory.repository_id == repository_id
        ).order_by(
            UserMemory.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()
        
        return results


# Singleton instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
