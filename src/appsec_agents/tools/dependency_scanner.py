import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
from dotenv import load_dotenv

# Get the Snyk organization from the environment variable
load_dotenv()
snyk_org = os.getenv("SNYK_ORG")


class DependencyVulnScanInput(BaseModel):
    local_path: str = Field(...,
                            description="Path to the locally cloned repository.")


class DependencyVulnScanTool(BaseTool):
    name: str = "Dependency Vulnerability Scanner"
    description: str = (
        "Scans the dependencies in a cloned repository for known vulnerabilities using Snyk."
    )
    args_schema: Type[BaseModel] = DependencyVulnScanInput

    def _run(self, local_path: str) -> str:
        """
        Run the Snyk CLI tool to scan the repository for vulnerabilities.
        """
        try:
            # Change to the repository directory
            command = ["snyk", "test",
                       f"--org={snyk_org}", "--all-projects", "--json"]
            result = subprocess.run(
                command,
                cwd=local_path,  # Set working directory to the repo path
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                return f"Snyk scan completed successfully:\n{result.stdout}"
            else:
                return f"Snyk scan failed with errors:\n{result.stderr}"
        except FileNotFoundError:
            return (
                "Snyk CLI tool not found. Ensure it is installed and added to the system PATH. "
                "Refer to https://snyk.io/ for installation instructions."
            )
        except Exception as e:
            return f"Error running Snyk scanner: {str(e)}"
