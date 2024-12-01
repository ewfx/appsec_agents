from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

class CloneGitHubRepoInput(BaseModel):
    """Input schema for CloneGitHubRepo."""
    repo_url: str = Field(..., description="The URL of the GitHub repository to clone.")
    destination: str = Field(..., description="The local directory to clone the repository into.")

class CloneGitHubRepoTool(BaseTool):
    name: str = "Clone GitHub Repository"
    description: str = (
        "This tool clones a GitHub repository to a local directory for analysis purposes. "
        "Provide the repository URL and the destination folder."
    )
    args_schema: Type[BaseModel] = CloneGitHubRepoInput

    def _run(self, repo_url: str, destination: str) -> str:
        try:
            # Ensure the destination directory exists
            os.makedirs(destination, exist_ok=True)
            
            # Clone the repository using git
            result = subprocess.run(
                ["git", "clone", repo_url, destination],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                logging.info(f"Repository successfully cloned to {destination}.")
                return f"Repository successfully cloned to {destination}."
            else:
                logging.error(f"Failed to clone repository. Error: {result.stderr}")
                return f"Failed to clone repository. Error: {result.stderr}"
        except Exception as e:
            logging.error(f"An error occurred while cloning the repository: {str(e)}")
            return f"An error occurred while cloning the repository: {str(e)}"

# Example usage
if __name__ == "__main__":
    tool = CloneGitHubRepoTool()
    result = tool._run("https://github.com/example/repo", "/path/to/destination")
    print(result)