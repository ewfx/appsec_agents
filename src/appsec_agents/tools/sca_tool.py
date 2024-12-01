from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os
from dotenv import load_dotenv

# Get the Snyk organization from the environment variable
load_dotenv()
snyk_org = os.getenv("SNYK_ORG")


class StaticCodeAnalysisInput(BaseModel):
    local_path: str = Field(...,
                            description="Path to the locally cloned repository.")


class StaticCodeAnalysisTool(BaseTool):
    name: str = "Static Code Analysis Tool"
    description: str = (
        "Runs a static analysis of the code using Snyk "
        "potential security vulnerabilities in the codebase."
    )
    args_schema: Type[BaseModel] = StaticCodeAnalysisInput

    def _run(self, local_path: str) -> str:
        try:
            # Use Snyk for SCA
            command = f"snyk code test --org={snyk_org} --all-projects"

            result = subprocess.run(command, cwd=local_path, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True, shell=True)

            if result.stderr == '':  # result.returncode is returning as 1 but the command is running fine
                return f"Static analysis completed successfully:\n{result.stdout}"
            else:
                return f"Static analysis failed:\n{result.stderr}"
        except Exception as e:
            return f"Error running static code analysis: {str(e)}"
