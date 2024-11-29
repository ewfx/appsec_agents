from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os

class DependencyVulnerabilityScanInput(BaseModel):
    repo_path: str = Field(..., description="Path to the locally cloned repository.")

class DependencyVulnerabilityScanTool(BaseTool):
    name: str = "Dependency Vulnerability Scanner"
    description: str = (
        "Scans the dependencies in a cloned repository for known vulnerabilities using tools like "
        "npm audit, pip-audit, or other language-specific scanners."
    )
    args_schema: Type[BaseModel] = DependencyVulnerabilityScanInput

    def _run(self, repo_path: str) -> str:
        try:
            # Run language-specific dependency scanner (example: pip-audit)
            result = subprocess.run(
                ["pip-audit", "--directory", repo_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                return f"Dependency scan completed successfully:\n{result.stdout}"
            else:
                return f"Dependency scan failed:\n{result.stderr}"
        except Exception as e:
            return f"Error running dependency scanner: {str(e)}"
