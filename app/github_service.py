from github import Github
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GitHubService:
    def __init__(self, client: Github):
        self.client = client
    
    def get_pr_diff(self, repo_name: str, pr_number: int) -> str:
        """Get the full diff for a PR."""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Get the diff using the API
            files = pr.get_files()
            
            diff_parts = []
            for file in files:
                if file.patch:  # Only files with actual changes
                    diff_parts.append(f"--- a/{file.filename}")
                    diff_parts.append(f"+++ b/{file.filename}")
                    diff_parts.append(file.patch)
                    diff_parts.append("")
            
            return "\n".join(diff_parts)
        except Exception as e:
            logger.error(f"Error getting PR diff: {e}")
            raise
    
    def get_pr_files(self, repo_name: str, pr_number: int, max_files: int = 10) -> List[Dict]:
        """Get changed files in a PR."""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            files = pr.get_files()
            
            result = []
            for idx, file in enumerate(files):
                if idx >= max_files:
                    break
                
                result.append({
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch,
                    "sha": file.sha
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting PR files: {e}")
            raise
    
    def get_file_content(self, repo_name: str, file_path: str, ref: str) -> str:
        """Get the content of a file at a specific commit."""
        try:
            repo = self.client.get_repo(repo_name)
            content = repo.get_contents(file_path, ref=ref)
            
            if isinstance(content, list):
                return ""  # It's a directory
            
            return content.decoded_content.decode('utf-8')
        except Exception as e:
            logger.warning(f"Could not get file content for {file_path}: {e}")
            return ""
    
    def post_review_comment(
        self,
        repo_name: str,
        pr_number: int,
        body: str,
        commit_id: str,
        path: str,
        line: Optional[int] = None
    ):
        """Post a review comment on a specific line or file."""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            if line:
                # Inline comment on specific line
                pr.create_review_comment(
                    body=body,
                    commit=repo.get_commit(commit_id),
                    path=path,
                    line=line
                )
            else:
                # General file comment
                pr.create_issue_comment(body)
            
            logger.info(f"Posted review comment on PR #{pr_number}")
        except Exception as e:
            logger.error(f"Error posting review comment: {e}")
            raise
    
    def post_pr_review(
        self,
        repo_name: str,
        pr_number: int,
        commit_id: str,
        body: str,
        event: str = "COMMENT",
        comments: Optional[List[Dict]] = None
    ):
        """
        Post a complete PR review.
        
        event can be: APPROVE, REQUEST_CHANGES, or COMMENT
        """
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Format comments for GitHub API
            review_comments = []
            if comments:
                for comment in comments:
                    if comment.get("line"):
                        review_comments.append({
                            "path": comment["path"],
                            "line": comment["line"],
                            "body": comment["body"]
                        })
            
            # Create the review
            if review_comments:
                pr.create_review(
                    commit=repo.get_commit(commit_id),
                    body=body,
                    event=event,
                    comments=review_comments
                )
            else:
                # Just post a comment if no inline comments
                pr.create_issue_comment(body)
            
            logger.info(f"Posted review on PR #{pr_number} with {len(review_comments)} comments")
        except Exception as e:
            logger.error(f"Error posting PR review: {e}")
            raise
    
    def get_pr_info(self, repo_name: str, pr_number: int) -> Dict:
        """Get PR metadata."""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            return {
                "title": pr.title,
                "description": pr.body or "",
                "author": pr.user.login,
                "head_sha": pr.head.sha,
                "base_sha": pr.base.sha,
                "state": pr.state,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting PR info: {e}")
            raise
