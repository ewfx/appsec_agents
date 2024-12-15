from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from git import Repo, GitCommandError
import logging
import subprocess
import shlex

# Set up logging
logger = logging.getLogger(__name__)


class GitToolInput(BaseModel):
    """Input schema for CommitChanges."""
    local_path: str = Field(...,
                            description="The local path to the Git repository.")
    git_command: str = Field(...,
                             description="The git command to run.")


class GitTool(BaseTool):
    name: str = "Git Tool"
    description: str = (
        "This tool lets you execute any git commands. "
    )
    args_schema: Type[BaseModel] = GitToolInput

    def _run(self, local_path: str, git_command: str) -> str:
        try:
            result = subprocess.run(
                ["git"] + shlex.split(git_command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=local_path
            )

            if result.returncode == 0:
                print(f"Git command executed: {result.args}")
                return f"Executed command successfully:\n{result.stdout}"
            else:
                print(f"Git command executed: {result.args}")
                print(f"Command output: {result.stdout}")
                return f"An error occurred:\n{result.stderr}"

        except GitCommandError as e:
            logger.error(f"Git error occurred: {e}")
            return f"Failed to executed command. Git error: {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return f"An error occurred while executing command: {e}"


# Example usage
if __name__ == "__main__":
    tool = GitTool()
    result = tool._run(
        local_path="/temp/appsec_sample_code",
        commit_message="add .",
    )
    print(result)
