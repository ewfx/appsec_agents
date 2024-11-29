from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os

class CodeEditorToolInput(BaseModel):
    """Input schema for CodeEditorTool."""
    file_path: str = Field(..., description="Path to the file that needs to be edited.")
    edit_instructions: str = Field(..., description="Instructions for the changes to be made in the file.")
    backup_file: bool = Field(default=True, description="Whether to create a backup of the file before editing.")

class CodeEditorTool(BaseTool):
    name: str = "Code Editor Tool"
    description: str = (
        "Allows the agent to programmatically modify a source code file based on provided instructions."
    )
    args_schema: Type[BaseModel] = CodeEditorToolInput

    def _run(self, file_path: str, edit_instructions: str, backup_file: bool = True) -> str:
        """
        Edits the specified file based on the given instructions.
        """
        try:
            # Ensure the file exists
            if not os.path.exists(file_path):
                return f"Error: File not found at path {file_path}"

            # Read the original file content
            with open(file_path, 'r') as f:
                original_content = f.read()

            # Optionally back up the original file
            if backup_file:
                backup_path = file_path + ".bak"
                with open(backup_path, 'w') as backup:
                    backup.write(original_content)
                backup_status = f"Backup created at {backup_path}."
            else:
                backup_status = "No backup was created."

            # Process the edit instructions (example using a simple pattern replacement)
            # In real scenarios, this might involve LLM APIs or custom parsers to modify code
            modified_content = self._apply_edits(original_content, edit_instructions)

            # Write the modified content back to the file
            with open(file_path, 'w') as f:
                f.write(modified_content)

            return f"File successfully modified: {file_path}. {backup_status}"

        except Exception as e:
            return f"Error while editing the file: {e}"

    def _apply_edits(self, content: str, instructions: str) -> str:
        """
        Simulates applying edits to the content based on instructions.
        You can replace this with advanced parsing logic or integrate LLM-based processing.
        """
        # Example: Simple string replacement for demonstration purposes
        if "replace" in instructions.lower():
            # Parse the "replace" instructions (e.g., "Replace 'foo' with 'bar'")
            try:
                _, target, _, replacement = instructions.split("'")
                return content.replace(target, replacement)
            except ValueError:
                raise ValueError("Invalid replace instruction format. Use: Replace 'old' with 'new'.")
        else:
            # Handle other types of instructions
            return f"# TODO: Apply edits based on these instructions: {instructions}\n" + content
