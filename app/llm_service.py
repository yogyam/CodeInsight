from anthropic import Anthropic
from typing import List, Dict, Optional
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model
    
    async def generate_review(
        self,
        code_diff: str,
        file_path: str,
        context: Optional[str] = None,
        user_memory: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate a code review using Claude Sonnet 4.5.
        
        Args:
            code_diff: The git diff of the file
            file_path: Path to the file being reviewed
            context: Additional context from RAG retrieval
            user_memory: User-specific memory/preferences
            
        Returns:
            Dictionary with review comments and suggestions
        """
        # Build the prompt
        system_prompt = """You are an expert code reviewer with deep knowledge of software engineering best practices.
Your role is to provide constructive, actionable feedback on pull requests.

Focus on:
- Code quality and maintainability
- Potential bugs and edge cases
- Security vulnerabilities
- Performance issues
- Best practices and patterns
- Documentation and comments

Provide specific, line-level suggestions when possible.
Be constructive and educational in your feedback."""

        user_prompt = f"""Review the following code changes:

File: {file_path}

Code Diff:
```
{code_diff}
```
"""

        if context:
            user_prompt += f"\n\nRelevant codebase context:\n{context}"
        
        if user_memory:
            user_prompt += f"\n\nUser preferences and history:\n{user_memory}"
        
        user_prompt += """

Please provide a detailed review with:
1. Overall assessment
2. Specific issues or concerns (with line numbers if applicable)
3. Suggestions for improvement
4. Positive observations

Format your response as JSON with the following structure:
{
  "overall_assessment": "Brief summary",
  "issues": [
    {
      "line": number or null,
      "severity": "critical|major|minor|suggestion",
      "description": "Issue description",
      "suggestion": "How to fix"
    }
  ],
  "positive_notes": ["List of good practices observed"]
}
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Parse the response
            review_text = response.content[0].text
            
            # Try to parse as JSON, fallback to text if fails
            import json
            try:
                review_data = json.loads(review_text)
            except json.JSONDecodeError:
                review_data = {
                    "overall_assessment": review_text[:200],
                    "issues": [],
                    "positive_notes": [],
                    "raw_text": review_text
                }
            
            return review_data
            
        except Exception as e:
            logger.error(f"Error generating review: {e}")
            raise
    
    async def summarize_pr(
        self,
        pr_title: str,
        pr_description: str,
        file_changes: List[str]
    ) -> str:
        """Generate a summary of the PR changes."""
        prompt = f"""Summarize this pull request:

Title: {pr_title}
Description: {pr_description}

Files changed:
{chr(10).join(f"- {f}" for f in file_changes)}

Provide a concise summary of what this PR does and its potential impact.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error summarizing PR: {e}")
            return "Unable to generate summary"


# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
