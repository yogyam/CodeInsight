from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
import hmac
import hashlib
from typing import Optional
from app.config import get_settings
from app.database import init_db
from app.tasks import process_pr_review, process_review_command
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Persistent Memory PR Review Bot",
    description="GitHub PR review bot with persistent memory",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    logger.info("Database initialized")


def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature:
        return False
    
    expected_signature = "sha256=" + hmac.new(
        settings.github_webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Persistent Memory PR Review Bot",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "celery": "running"
    }


@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Handle GitHub webhook events.
    
    Supported events:
    - pull_request (opened, synchronize, reopened)
    - issue_comment (created) - for /review commands
    """
    # Read payload
    payload = await request.body()
    
    # Verify signature
    if not verify_github_signature(payload, x_hub_signature_256):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse JSON payload
    event_data = await request.json()
    
    logger.info(f"Received webhook event: {x_github_event}")
    
    # Handle pull_request events
    if x_github_event == "pull_request":
        action = event_data.get("action")
        
        if action in ["opened", "synchronize", "reopened"] and settings.auto_review_enabled:
            pr_data = {
                "pr_number": event_data["pull_request"]["number"],
                "repository": event_data["repository"]["full_name"],
                "repository_id": str(event_data["repository"]["id"]),
                "installation_id": event_data["installation"]["id"],
                "author": event_data["pull_request"]["user"]["login"],
                "head_sha": event_data["pull_request"]["head"]["sha"],
                "base_sha": event_data["pull_request"]["base"]["sha"],
            }
            
            # Enqueue review task
            task = process_pr_review.delay(pr_data)
            logger.info(f"Enqueued PR review task: {task.id}")
            
            return JSONResponse({
                "status": "queued",
                "task_id": task.id,
                "pr_number": pr_data["pr_number"]
            })
    
    # Handle issue_comment events (for /review command)
    elif x_github_event == "issue_comment":
        action = event_data.get("action")
        comment_body = event_data.get("comment", {}).get("body", "").strip()
        
        if action == "created" and comment_body.startswith(settings.review_command):
            # Check if comment is on a PR
            if "pull_request" in event_data.get("issue", {}):
                pr_url = event_data["issue"]["pull_request"]["url"]
                
                review_data = {
                    "pr_number": event_data["issue"]["number"],
                    "repository": event_data["repository"]["full_name"],
                    "repository_id": str(event_data["repository"]["id"]),
                    "installation_id": event_data["installation"]["id"],
                    "commenter": event_data["comment"]["user"]["login"],
                }
                
                # Enqueue review command task
                task = process_review_command.delay(review_data)
                logger.info(f"Enqueued review command task: {task.id}")
                
                return JSONResponse({
                    "status": "queued",
                    "task_id": task.id,
                    "pr_number": review_data["pr_number"]
                })
    
    # Event not handled
    return JSONResponse({"status": "ignored", "event": x_github_event})


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
