from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from git import Repo, GitCommandError
import os
import shutil
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
            # Check if the directory exists and remove it if necessary
            if os.path.exists(local_path):
                logger.info(f"Removing existing directory at {local_path}")
                shutil.rmtree(local_path)

            # Clone the repository
            logger.info(f"Cloning repository from {repo_url} to {local_path}")
            repo = Repo.clone_from(repo_url, local_path)
            logger.info(f"Repository successfully cloned to {local_path}")

            # Create and checkout new branch
            try:
                new_branch = repo.create_head('vuln_fix')
                new_branch.checkout()
                logger.info("Created and checked out 'vuln_fix' branch")
                return f"Repository successfully cloned to {local_path} and created/checked out 'vuln_fix' branch."
            except Exception as branch_error:
                logger.error(
                    f"Error creating/checking out branch: {branch_error}")
                return f"Repository cloned but failed to create/checkout branch: {branch_error}"

        except GitCommandError as e:
            logger.error(f"Git error occurred: {e}")
            return f"Failed to clone repository. Git error: {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return f"An error occurred while cloning the repository: {e}"


# Example usage
if __name__ == "__main__":
    tool = CloneGitHubRepoTool()
    result = tool._run(
        'https://github.com/ewfx/appsec_sample_code', "/temp/appsec_sample_code")
    print(result)
