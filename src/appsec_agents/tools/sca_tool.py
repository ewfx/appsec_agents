from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os

class StaticCodeAnalysisInput(BaseModel):
    repo_path: str = Field(..., description="Path to the locally cloned repository.")
    tool_name: str = Field(..., description="The static analysis tool to use (e.g., Bandit, ESLint).")

class StaticCodeAnalysisTool(BaseTool):
    name: str = "Static Code Analysis Tool"
    description: str = (
        "Runs a static analysis tool (like Bandit for Python or ESLint for JavaScript) to identify "
        "potential security vulnerabilities in the codebase."
    )
    args_schema: Type[BaseModel] = StaticCodeAnalysisInput

    def _run(self, repo_path: str, tool_name: str) -> str:
        try:
            # Example: Using Bandit for Python
            if tool_name.lower() == "bandit":
                result = subprocess.run(
                    ["bandit", "-r", repo_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                return f"Unsupported tool: {tool_name}. Add support for additional tools as needed."

            if result.returncode == 0:
                return f"Static analysis completed successfully:\n{result.stdout}"
            else:
                return f"Static analysis failed:\n{result.stderr}"
        except Exception as e:
            return f"Error running static code analysis: {str(e)}"
