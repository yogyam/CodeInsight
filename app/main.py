from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from app.config import get_settings
from app.database import init_db
from app.tasks import process_pr_review, process_review_command
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
security = HTTPBearer()

app = FastAPI(
    title="Persistent Memory PR Review Bot",
    description="GitHub PR review bot with persistent memory (GitHub Actions triggered)",
    version="2.0.0"
)


class ReviewRequest(BaseModel):
    """Request model for PR review trigger."""
    owner: str
    repo: str
    pr_number: int
    installation_id: int


class ReviewCommandRequest(BaseModel):
    """Request model for manual review command."""
    owner: str
    repo: str
    pr_number: int
    installation_id: int
    comment_body: str


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    logger.info("Database initialized")


def verify_api_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify Bearer token from GitHub Actions."""
    if credentials.credentials != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return True


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Persistent Memory PR Review Bot",
        "version": "2.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "celery": "running"
    }


@app.post("/api/review")
async def trigger_review(
    request: ReviewRequest,
    authorized: bool = Depends(verify_api_token)
):
    """
    Trigger a PR review (called by GitHub Actions).
    
    This endpoint is called by the pr-review.yml workflow
    when a PR is opened, synchronized, or reopened.
    """
    logger.info(f"Review requested for {request.owner}/{request.repo}#{request.pr_number}")
    
    # Build pr_data for task
    pr_data = {
        "pr_number": request.pr_number,
        "repository": f"{request.owner}/{request.repo}",
        "repository_id": f"{request.owner}/{request.repo}",  # Simplified
        "installation_id": request.installation_id,
    }
    
    # Enqueue review task
    task = process_pr_review.delay(pr_data)
    logger.info(f"Enqueued PR review task: {task.id}")
    
    return JSONResponse({
        "status": "queued",
        "task_id": task.id,
        "pr_number": pr_data["pr_number"]
    })


@app.post("/api/review/command")
async def trigger_review_command(
    request: ReviewCommandRequest,
    authorized: bool = Depends(verify_api_token)
):
    """
    Trigger a manual review via /review command (called by GitHub Actions).
    
    This endpoint is called by the review-command.yml workflow
    when a user comments /review on a PR.
    """
    logger.info(f"Manual review requested for {request.owner}/{request.repo}#{request.pr_number}")
    
    review_data = {
        "pr_number": request.pr_number,
        "repository": f"{request.owner}/{request.repo}",
        "repository_id": f"{request.owner}/{request.repo}",
        "installation_id": request.installation_id,
        "commenter": "github-actions",  # From GitHub Actions
    }
    
    # Enqueue review command task
    task = process_review_command.delay(review_data)
    logger.info(f"Enqueued review command task: {task.id}")
    
    return JSONResponse({
        "status": "queued",
        "task_id": task.id,
        "pr_number": review_data["pr_number"]
    })


@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Check the status of a review task."""
    from app.celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
