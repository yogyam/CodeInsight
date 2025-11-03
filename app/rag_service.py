from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.database import SessionLocal, CodeEmbedding
from app.embedding_service import get_embedding_service
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGService:
    """Retrieval-Augmented Generation service for codebase context."""
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
    
    async def index_code_file(
        self,
        db: Session,
        repository_id: str,
        file_path: str,
        content: str,
        chunk_size: int = 500
    ):
        """
        Index a code file by splitting it into chunks and storing embeddings.
        """
        # Split content into chunks (simple line-based splitting)
        lines = content.split('\n')
        chunks = []
        
        current_chunk = []
        current_size = 0
        
        for line in lines:
            current_chunk.append(line)
            current_size += len(line)
            
            if current_size >= chunk_size:
                chunk_text = '\n'.join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = []
                current_size = 0
        
        # Add remaining lines
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # Store chunks with embeddings
        for idx, chunk in enumerate(chunks):
            if chunk.strip():  # Skip empty chunks
                await self.embedding_service.store_code_embedding(
                    db=db,
                    repository_id=repository_id,
                    file_path=file_path,
                    code_chunk=chunk,
                    metadata={
                        "chunk_index": idx,
                        "total_chunks": len(chunks)
                    }
                )
        
        logger.info(f"Indexed {len(chunks)} chunks from {file_path}")
    
    async def retrieve_relevant_context(
        self,
        db: Session,
        repository_id: str,
        query: str,
        max_chunks: int = 5
    ) -> str:
        """
        Retrieve relevant code context for a query.
        """
        # Search for similar code chunks
        similar_chunks = await self.embedding_service.search_similar_code(
            db=db,
            repository_id=repository_id,
            query=query,
            limit=max_chunks
        )
        
        if not similar_chunks:
            return ""
        
        # Format context
        context_parts = []
        for chunk in similar_chunks:
            context_parts.append(f"From {chunk.file_path}:")
            context_parts.append(chunk.code_chunk)
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    async def get_related_files(
        self,
        db: Session,
        repository_id: str,
        changed_files: List[str]
    ) -> List[str]:
        """
        Find files related to the changed files based on similarity.
        """
        # Get embeddings for changed files
        related = set()
        
        for file_path in changed_files[:5]:  # Limit to prevent too many queries
            # Query for similar code in other files
            chunks = db.query(CodeEmbedding).filter(
                CodeEmbedding.repository_id == repository_id,
                CodeEmbedding.file_path != file_path
            ).limit(10).all()
            
            for chunk in chunks:
                related.add(chunk.file_path)
        
        return list(related)[:10]  # Return top 10 related files


# Singleton instance
_rag_service = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
