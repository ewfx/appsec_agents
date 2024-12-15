import os
import json
import asyncio
from typing import Dict, List, TypedDict, Any
from crewai.tools import BaseTool
from dotenv import load_dotenv
import google.generativeai as genai
import typing_extensions as typing
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class NewFileContent(TypedDict):
    new_file_content: str


class FileFixInfo(BaseModel):
    filepath: str
    filename: str
    issue: str
    how_to_fix: str


class FixSingleFileToolInput(BaseModel):
    """Input schema for FixSingleFileTool."""
    files: Any = Field(...,
                       description="The URL of the GitHub repository to clone.")


class FixSingleFileTool(BaseTool):
    name: str = "Fix single file"
    description: str = "Fixes security vulnerabilities in files using Gemini API"

    def _run(self, files: Any) -> List[Dict]:
        """Synchronous wrapper for the async file fixing functionality"""

        async def _async_fix_files():
            model = genai.GenerativeModel("gemini-1.5-flash")
            genai.configure(api_key=os.getenv("API_KEY"))

            for file in files:
                try:
                    # Read the current file content
                    with open(file['filepath'], 'r') as f:
                        current_content = f.read()

                    # Construct the prompt for Gemini
                    prompt = f"""
                    Task: Fix the security vulnerabilities in this file.

                    Current File Content:
                    {current_content}

                    Suggested Fix:
                    {file['how_to_fix']}

                    Please provide only the complete fixed file content in a JSON response with the format:
                    {{"new_file_content": "FIXED FILE CONTENT HERE"}}
                    """

                    # Get response from Gemini in JSON mode
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=NewFileContent
                        ),
                    )

                    print(response)

                    # Parse the response
                    try:
                        fixed_content = json.loads(response.text)[
                            'new_file_content']

                        # Write the fixed content back to the file
                        with open(file['filepath'], 'w') as f:
                            f.write(fixed_content)

                        # Mark the file as fixed
                        file['wasFixed'] = True

                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Error parsing Gemini response for file {
                              file['filepath']}: {e}")
                        file['wasFixed'] = False

                except Exception as e:
                    print(f"Error processing file {file['filepath']}: {e}")
                    file['wasFixed'] = False

            return files

        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run the coroutine using the event loop
        loop.run_until_complete(_async_fix_files())

        return files


# Example usage
if __name__ == "__main__":
    tool = FixSingleFileTool()
    result = tool._run([])
    print(result)
