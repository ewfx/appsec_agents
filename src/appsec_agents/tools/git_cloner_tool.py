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
    repo_url: str = Field(...,
                          description="The URL of the GitHub repository to clone.")
    local_path: str = Field(...,
                            description="The local directory to clone the repository into.")


class CloneGitHubRepoTool(BaseTool):
    name: str = "Clone GitHub Repository"
    description: str = (
        "This tool clones a GitHub repository to a local directory for analysis purposes. "
        "Provide the repository URL and the local_path folder."
    )
    args_schema: Type[BaseModel] = CloneGitHubRepoInput

    def _run(self, repo_url: str, local_path: str) -> str:
        try:
            # Check if local_path directory exists and remove it if it does
            if os.path.exists(local_path):
                logging.info(f"Removing existing directory at {local_path}")
                subprocess.run(["rm", "-rf", local_path], check=True)

            # Create the local_path directory
            os.makedirs(local_path)

            # Clone the repository using git
            result = subprocess.run(
                ["git", "clone", repo_url, local_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                logging.info(f"Repository successfully cloned to {
                             local_path}.")
                return f"Repository successfully cloned to {local_path}."
            else:
                logging.error(f"Failed to clone repository. Error: {
                              result.stderr}")
                return f"Failed to clone repository. Error: {result.stderr}"
        except Exception as e:
            logging.error(
                f"An error occurred while cloning the repository: {str(e)}")
            return f"An error occurred while cloning the repository: {str(e)}"


# Example usage
if __name__ == "__main__":
    tool = CloneGitHubRepoTool()
    result = tool._run("https://github.com/example/repo",
                       "/path/to/local_path")
    print(result)
