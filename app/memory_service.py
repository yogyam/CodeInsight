from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import UserMemory, PRReview
from app.embedding_service import get_embedding_service
import logging
import json

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing persistent user and repository memory."""
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
    
    async def store_user_preference(
        self,
        db: Session,
        user_id: str,
        repository_id: str,
        preference_type: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Store a user preference or pattern."""
        embedding = self.embedding_service.create_embedding(content)
        
        memory = UserMemory(
            user_id=user_id,
            repository_id=repository_id,
            memory_type=preference_type,
            content=content,
            metadata=metadata or {},
            embedding=embedding
        )
        
        db.add(memory)
        db.commit()
        
        logger.info(f"Stored user preference for {user_id} in {repository_id}")
        return memory
    
    async def get_user_context(
        self,
        db: Session,
        user_id: str,
        repository_id: str,
        query: Optional[str] = None
    ) -> str:
        """Retrieve relevant user context."""
        if query:
            # Use semantic search
            memories = await self.embedding_service.search_user_memory(
                db, user_id, repository_id, query
            )
        else:
            # Get recent memories
            memories = db.query(UserMemory).filter(
                UserMemory.user_id == user_id,
                UserMemory.repository_id == repository_id
            ).order_by(UserMemory.updated_at.desc()).limit(5).all()
        
        if not memories:
            return ""
        
        # Format memories into context
        context_parts = []
        for mem in memories:
            context_parts.append(f"- {mem.memory_type}: {mem.content}")
        
        return "\n".join(context_parts)
    
    async def store_review_history(
        self,
        db: Session,
        pr_number: int,
        repository_id: str,
        user_id: str,
        review_content: str,
        comments_count: int
    ):
        """Store PR review history."""
        review = PRReview(
            pr_number=pr_number,
            repository_id=repository_id,
            user_id=user_id,
            review_content=review_content,
            comments_count=comments_count
        )
        
        db.add(review)
        db.commit()
        
        return review
    
    async def learn_from_feedback(
        self,
        db: Session,
        user_id: str,
        repository_id: str,
        feedback_type: str,
        context: Dict
    ):
        """
        Learn from user interactions and feedback.
        
        Examples:
        - User dismisses certain types of suggestions
        - User approves specific patterns
        - User adds clarifying comments
        """
        content = json.dumps(context)
        
        await self.store_user_preference(
            db,
            user_id,
            repository_id,
            f"feedback_{feedback_type}",
            content,
            {"learned_at": datetime.utcnow().isoformat()}
        )
    
    async def get_pr_history(
        self,
        db: Session,
        repository_id: str,
        user_id: str,
        limit: int = 10
    ) -> List[PRReview]:
        """Get recent PR review history for a user."""
        return db.query(PRReview).filter(
            PRReview.repository_id == repository_id,
            PRReview.user_id == user_id
        ).order_by(PRReview.created_at.desc()).limit(limit).all()


# Singleton instance
_memory_service = None

def get_memory_service() -> MemoryService:
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
