from app.celery_app import celery_app
from app.database import SessionLocal
from app.github_auth import get_github_client
from app.github_service import GitHubService
from app.llm_service import get_llm_service
from app.memory_service import get_memory_service
from app.rag_service import get_rag_service
from app.config import get_settings
import logging
from typing import Dict

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, max_retries=3)
def process_pr_review(self, pr_data: Dict):
    """
    Process a PR review request.
    
    This is the main task that orchestrates the entire review process:
    1. Fetch PR diff and metadata
    2. Retrieve relevant codebase context (RAG)
    3. Get user memory/preferences
    4. Generate review using LLM
    5. Post review comments to GitHub
    6. Store review in memory
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Processing PR review for #{pr_data['pr_number']}")
        
        # Get GitHub client
        github_client = get_github_client(pr_data['installation_id'])
        github_service = GitHubService(github_client)
        
        # Get services
        llm_service = get_llm_service()
        memory_service = get_memory_service()
        rag_service = get_rag_service()
        
        # Get PR information
        pr_info = github_service.get_pr_info(
            pr_data['repository'],
            pr_data['pr_number']
        )
        
        # Get changed files
        changed_files = github_service.get_pr_files(
            pr_data['repository'],
            pr_data['pr_number'],
            max_files=settings.max_files_to_review
        )
        
        logger.info(f"Reviewing {len(changed_files)} files")
        
        # Get user context from memory
        user_context = ""
        if settings.enable_memory_persistence:
            import asyncio
            user_context = asyncio.run(memory_service.get_user_context(
                db=db,
                user_id=pr_data['author'],
                repository_id=pr_data['repository_id']
            ))
        
        # Process each file
        all_reviews = []
        review_comments = []
        
        for file_data in changed_files:
            if not file_data.get('patch'):
                continue
            
            # Check diff size
            if len(file_data['patch']) > settings.max_diff_size:
                logger.warning(f"Skipping {file_data['filename']}: diff too large")
                continue
            
            # Get relevant context from codebase
            codebase_context = ""
            if settings.enable_memory_persistence:
                import asyncio
                codebase_context = asyncio.run(rag_service.retrieve_relevant_context(
                    db=db,
                    repository_id=pr_data['repository_id'],
                    query=file_data['patch'][:500]  # Use first part of diff as query
                ))
            
            # Generate review
            import asyncio
            review = asyncio.run(llm_service.generate_review(
                code_diff=file_data['patch'],
                file_path=file_data['filename'],
                context=codebase_context,
                user_memory=user_context
            ))
            
            all_reviews.append({
                "file": file_data['filename'],
                "review": review
            })
            
            # Format comments for GitHub
            if review.get('issues'):
                for issue in review['issues']:
                    comment_body = f"**{issue['severity'].upper()}**: {issue['description']}\n\n"
                    if issue.get('suggestion'):
                        comment_body += f"💡 **Suggestion**: {issue['suggestion']}"
                    
                    comment = {
                        "path": file_data['filename'],
                        "body": comment_body,
                        "line": issue.get('line')
                    }
                    review_comments.append(comment)
        
        # Create overall review summary
        summary_parts = ["## 🤖 AI Code Review\n"]
        
        for file_review in all_reviews:
            summary_parts.append(f"### 📄 {file_review['file']}")
            summary_parts.append(file_review['review'].get('overall_assessment', 'No issues found'))
            
            if file_review['review'].get('positive_notes'):
                summary_parts.append("\n✅ **Good practices:**")
                for note in file_review['review']['positive_notes']:
                    summary_parts.append(f"- {note}")
            
            summary_parts.append("")
        
        summary = "\n".join(summary_parts)
        
        # Post review to GitHub
        github_service.post_pr_review(
            repo_name=pr_data['repository'],
            pr_number=pr_data['pr_number'],
            commit_id=pr_data['head_sha'],
            body=summary,
            event="COMMENT",
            comments=review_comments
        )
        
        # Store review in memory
        if settings.enable_memory_persistence:
            import asyncio
            asyncio.run(memory_service.store_review_history(
                db=db,
                pr_number=pr_data['pr_number'],
                repository_id=pr_data['repository_id'],
                user_id=pr_data['author'],
                review_content=summary,
                comments_count=len(review_comments)
            ))
        
        logger.info(f"Successfully completed review for PR #{pr_data['pr_number']}")
        
        return {
            "status": "success",
            "pr_number": pr_data['pr_number'],
            "files_reviewed": len(all_reviews),
            "comments_posted": len(review_comments)
        }
        
    except Exception as e:
        logger.error(f"Error processing PR review: {e}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def process_review_command(self, review_data: Dict):
    """
    Process a manual /review command on a PR.
    
    Similar to process_pr_review but triggered by explicit command.
    """
    # Reuse the PR review logic
    return process_pr_review(review_data)


@celery_app.task
def index_repository_code(repository_id: str, repository_name: str, installation_id: int):
    """
    Background task to index repository code for RAG.
    
    This can be run periodically or on-demand to update the code embeddings.
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Indexing repository: {repository_name}")
        
        github_client = get_github_client(installation_id)
        repo = github_client.get_repo(repository_name)
        rag_service = get_rag_service()
        
        # Get repository contents (limiting to main code files)
        contents = repo.get_contents("")
        indexed_count = 0
        
        while contents:
            file_content = contents.pop(0)
            
            if file_content.type == "dir":
                # Add directory contents to queue
                contents.extend(repo.get_contents(file_content.path))
            else:
                # Only index code files
                if file_content.path.endswith(('.py', '.js', '.ts', '.java', '.go', '.rb', '.cpp', '.c', '.h')):
                    try:
                        content = file_content.decoded_content.decode('utf-8')
                        
                        import asyncio
                        asyncio.run(rag_service.index_code_file(
                            db=db,
                            repository_id=repository_id,
                            file_path=file_content.path,
                            content=content
                        ))
                        
                        indexed_count += 1
                        
                        # Limit indexing to prevent overwhelming the system
                        if indexed_count >= 100:
                            logger.info(f"Reached indexing limit of 100 files")
                            break
                            
                    except Exception as e:
                        logger.warning(f"Could not index {file_content.path}: {e}")
        
        logger.info(f"Indexed {indexed_count} files from {repository_name}")
        
        return {
            "status": "success",
            "files_indexed": indexed_count
        }
        
    except Exception as e:
        logger.error(f"Error indexing repository: {e}", exc_info=True)
        raise
    
    finally:
        db.close()
