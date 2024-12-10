from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from git import Repo, GitCommandError
import logging

# Set up logging
logger = logging.getLogger(__name__)


class CommitChangesInput(BaseModel):
    """Input schema for CommitChanges."""
    local_path: str = Field(...,
                            description="The local path to the Git repository.")
    commit_message: str = Field(...,
                                description="The message for the commit.")
    branch_name: str = Field(default="vuln_fix",
                             description="The branch name to commit to (default: vuln_fix)")


class CommitChangesTool(BaseTool):
    name: str = "Commit Changes to Repository"
    description: str = (
        "This tool commits changes in a local Git repository. "
        "Provide the repository path, commit message, and optionally the branch name."
    )
    args_schema: Type[BaseModel] = CommitChangesInput

    def _run(self, local_path: str, commit_message: str, branch_name: str = "vuln_fix") -> str:
        try:
            # Open the repository
            logger.info(f"Opening repository at {local_path}")
            repo = Repo(local_path)

            # Check if there are any changes to commit
            if not repo.is_dirty(untracked_files=True):
                logger.info("No changes to commit")
                return "No changes detected in the repository."

            # Add all changes
            logger.info("Adding all changes to staging")
            repo.git.add(A=True)

            # Commit the changes
            logger.info(f"Committing changes with message: {commit_message}")
            repo.index.commit(commit_message)

            return f"Successfully committed changes with message: '{commit_message}' on branch '{branch_name}'"

        except GitCommandError as e:
            logger.error(f"Git error occurred: {e}")
            return f"Failed to commit changes. Git error: {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return f"An error occurred while committing changes: {e}"


# Example usage
if __name__ == "__main__":
    tool = CommitChangesTool()
    result = tool._run(
        local_path="/temp/appsec_sample_code",
        commit_message="Fix: Addressing security vulnerabilities",
        branch_name="vuln_fix"
    )
    print(result)
