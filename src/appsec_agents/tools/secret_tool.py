from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os

class SecretDetectionInput(BaseModel):
    repo_path: str = Field(..., description="Path to the locally cloned repository.")

class SecretDetectionTool(BaseTool):
    name: str = "Secret Detection Tool"
    description: str = (
        "Scans the repository for hardcoded secrets, API keys, and sensitive information "
        "using tools like truffleHog or git-secrets."
    )
    args_schema: Type[BaseModel] = SecretDetectionInput

    def _run(self, repo_path: str) -> str:
        try:
            # Example: Using truffleHog
            result = subprocess.run(
                ["trufflehog", "filesystem", "--directory", repo_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                return f"Secret detection completed successfully:\n{result.stdout}"
            else:
                return f"Secret detection failed:\n{result.stderr}"
        except Exception as e:
            return f"Error running secret detection: {str(e)}"
