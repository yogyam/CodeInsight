import time
import jwt
from github import Github, Auth, GithubIntegration
from typing import Optional
from pathlib import Path
from app.config import get_settings

settings = get_settings()


class GitHubAppAuth:
    def __init__(self):
        self.app_id = settings.github_app_id
        self.private_key_path = settings.github_app_private_key_path
        self._private_key = None
        
    def _load_private_key(self) -> str:
        """Load the GitHub App private key."""
        if self._private_key is None:
            key_path = Path(self.private_key_path)
            if key_path.exists():
                self._private_key = key_path.read_text()
            else:
                raise FileNotFoundError(f"Private key not found at {self.private_key_path}")
        return self._private_key
    
    def get_jwt(self) -> str:
        """Generate a JWT for GitHub App authentication."""
        private_key = self._load_private_key()
        
        payload = {
            "iat": int(time.time()),
            "exp": int(time.time()) + 600,  # 10 minutes
            "iss": self.app_id
        }
        
        return jwt.encode(payload, private_key, algorithm="RS256")
    
    def get_installation_client(self, installation_id: int) -> Github:
        """Get an authenticated GitHub client for a specific installation."""
        integration = GithubIntegration(
            integration_id=self.app_id,
            private_key=self._load_private_key()
        )
        
        auth = integration.get_access_token(installation_id)
        return Github(auth=Auth.Token(auth.token))
    
    def get_app_client(self) -> Github:
        """Get an authenticated GitHub client for the app itself."""
        jwt_token = self.get_jwt()
        return Github(auth=Auth.Token(jwt_token))


def get_github_client(installation_id: int) -> Github:
    """Helper function to get GitHub client for an installation."""
    auth = GitHubAppAuth()
    return auth.get_installation_client(installation_id)
