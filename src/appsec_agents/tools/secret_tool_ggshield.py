from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
from pathlib import Path
import sys
import os
import time

class GgShieldInput(BaseModel):
    local_path: str = Field(..., description="Path to the locally cloned Git repository.")

class GgShieldTool(BaseTool):
    name: str = "Secret Detection Tool (ggshield)"
    description: str = (
        "Scans a Git repository for hardcoded secrets, API keys, and sensitive information "
        "using the GitGuardian CLI tool (ggshield)."
    )
    args_schema: Type[BaseModel] = GgShieldInput

    def _run(self, local_path: str) -> str:
        """Runs ggshield to scan for secrets in the specified Git repository."""
        path = Path(local_path).resolve()

        # Ensure the provided path exists and is a valid Git repository
        if not path.is_dir():
            return f"Error: The provided path '{local_path}' is not a valid directory."
        if not (path / ".git").exists():
            return f"Error: The provided path '{local_path}' is not a valid Git repository."

        try:
            # Get the path to the virtual environment's Scripts directory
            venv_scripts_path = os.path.join(os.path.dirname(sys.executable), 'Scripts')
            os.environ['PATH'] = venv_scripts_path + os.pathsep + os.environ['PATH']

            # Run ggshield secret scan command with --yes flag to bypass prompts
            command = ["ggshield", "secret", "scan", "path", str(path), "--recursive", "--yes"]
            print(f"Executing command: {' '.join(command)}")  # Print the command being executed

            # Start the command in a separate process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Read and print output incrementally
            stdout_lines = []
            stderr_lines = []
            start_time = time.time()
            while process.poll() is None:
                if time.time() - start_time > 30:
                    process.terminate()
                    return "Error: The command timed out after 30 seconds."

                # Read stdout and stderr incrementally
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()

                if stdout_line:
                    print(stdout_line, end='')
                    stdout_lines.append(stdout_line)
                if stderr_line:
                    print(stderr_line, end='')
                    stderr_lines.append(stderr_line)

                time.sleep(0.1)

            # Read any remaining output
            stdout, stderr = process.communicate()
            if stdout:
                print(stdout, end='')
                stdout_lines.append(stdout)
            if stderr:
                print(stderr, end='')
                stderr_lines.append(stderr)

            if process.returncode == 0:
                return f"Secret detection completed successfully:\n{''.join(stdout_lines)}"
            else:
                return f"Secret detection failed:\n{''.join(stderr_lines)}"
        except subprocess.TimeoutExpired:
            return "Error: The command timed out after 30 seconds."
        except FileNotFoundError:
            return "Error: The tool 'ggshield' is not installed or not in the system PATH."
        except Exception as e:
            return f"Unexpected error occurred during secret detection: {str(e)}"

# Example usage
if __name__ == "__main__":
    tool = GgShieldTool()
    result = tool._run("/temp/appsec_sample_code")
    print(result)