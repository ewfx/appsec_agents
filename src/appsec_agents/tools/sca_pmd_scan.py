from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os


class PMDStaticCodeAnalysisInput(BaseModel):
    local_path: str = Field(...,
                            description="Path to the locally cloned repository.")


class PMDStaticCodeAnalysisTool(BaseTool):
    name: str = "Static Code Analysis using PMD"
    description: str = (
        "Runs a static analysis of the code using PMD and provides input on best practices, security, error prone code and performance."
    )
    args_schema: Type[BaseModel] = PMDStaticCodeAnalysisInput

    def _run(self, local_path: str) -> str:
        try:
            command = f"pmd check -f text -R category/java/errorprone.xml,category/java/bestpractices.xml,category/java/security.xml,category/java/performance.xml  -d {
                local_path}/src/main/java -r report.txt --no-cache"

            result = subprocess.run(command, cwd=local_path, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True, shell=True)

            # Read the report file content
            try:
                with open(os.path.join(local_path, "report.txt"), "r") as report_file:
                    report_content = report_file.read()

                # Delete the report file
                os.remove(os.path.join(local_path, "report.txt"))

                # Add report content to result stdout
                result.stdout = report_content
            except FileNotFoundError:
                # If report file wasn't created, continue without modification
                pass

            if result.stderr == '':  # result.returncode is returning as 4 but the command is running fine
                return f"Static analysis completed successfully:\n{result.stdout}"
            else:
                return f"Static analysis failed:\n{result.stderr}"
        except Exception as e:
            return f"Error running static code analysis: {str(e)}"
