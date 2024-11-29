from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os

class GitPRToolInput(BaseModel):
    """Input schema for creating a pull request."""
    repository_path: str = Field(..., description="Path to the cloned repository.")
    branch_name: str = Field(..., description="The name of the branch to create.")
    commit_message: str = Field(..., description="Commit message for the changes.")
    pr_title: str = Field(..., description="Title for the pull request.")
    pr_description: str = Field(..., description="Description of the pull request.")

class GitPRTool(BaseTool):
    name: str = "Git Pull Request Tool"
    description: str = (
        "Creates a new Git branch, commits changes, pushes the branch, and creates a pull request."
    )
    args_schema: Type[BaseModel] = GitPRToolInput

    def _run(self, repository_path: str, branch_name: str, commit_message: str, pr_title: str, pr_description: str) -> str:
        try:
            # Navigate to the repository path
            os.chdir(repository_path)
            
            # Create and checkout a new branch
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)

            # Stage all changes
            subprocess.run(["git", "add", "."], check=True)

            # Commit the changes
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # Push the branch
            subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], check=True)

            # Assuming a GitHub CLI (gh) is installed to create a pull request
            pr_output = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", pr_title,
                    "--body", pr_description
                ],
                check=True,
                capture_output=True,
                text=True
            )

            return pr_output.stdout.strip()  # Returns the PR URL

        except subprocess.CalledProcessError as e:
            return f"Error while creating pull request: {e}"
