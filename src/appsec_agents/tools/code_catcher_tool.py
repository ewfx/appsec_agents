from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os

class CodePatternMatcherInput(BaseModel):
    repo_path: str = Field(..., description="Path to the locally cloned repository.")
    pattern: str = Field(..., description="Regex pattern to search for in the codebase.")

class CodePatternMatcherTool(BaseTool):
    name: str = "Custom Code Pattern Matcher"
    description: str = (
        "Searches the codebase for specific patterns (e.g., usage of dangerous functions like eval()). "
        "Useful for identifying insecure code practices."
    )
    args_schema: Type[BaseModel] = CodePatternMatcherInput

    def _run(self, repo_path: str, pattern: str) -> str:
        try:
            result = subprocess.run(
                ["grep", "-r", pattern, repo_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                return f"Pattern matching completed successfully:\n{result.stdout}"
            else:
                return f"No matches found for the pattern '{pattern}' or an error occurred:\n{result.stderr}"
        except Exception as e:
            return f"Error running pattern matcher: {str(e)}"
