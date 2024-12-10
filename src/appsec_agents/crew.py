import logging
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.flow.flow import listen
from crewai_tools import FileReadTool
from crewai_tools import FileWriterTool

from pydantic import BaseModel
from typing import List

# Import custom tools for the project
from appsec_agents.tools.git_pr_tool import GitPRTool
from appsec_agents.tools.git_cloner_tool import CloneGitHubRepoTool
from appsec_agents.tools.dependency_scanner import DependencyVulnScanTool
from appsec_agents.tools.sca_tool import StaticCodeAnalysisTool
from appsec_agents.tools.fix_single_file import FixSingleFileTool
from appsec_agents.tools.git_commit_tool import CommitChangesTool
from appsec_agents.tools.sca_pmd_scan import PMDStaticCodeAnalysisTool
from appsec_agents.tools.secret_tool import SecretDetectionTool

logger = logging.getLogger(__name__)


class FileFixInfo(BaseModel):
    filepath: str
    filename: str
    issue: str
    how_to_fix: str


class FilesToFix(BaseModel):
    files: List[FileFixInfo]
    commit_message: str


@CrewBase
class AppsecAgents():
    """AppsecAgents crew for identifying, diagnosing, and fixing security vulnerabilities."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @before_kickoff  # Hook to execute before the crew starts
    def setup_environment(self, inputs):
        """Prepare the environment or inputs before kickoff."""
        logger.info(
            "Setting up the environment for the security analysis crew...")
        # Example of dynamically added input
        return inputs

    @after_kickoff  # Hook to execute after the crew finishes
    def summarize_results(self, output):
        """Log or summarize results after the crew finishes."""
        logger.info(f"Security Analysis Results: {output}")
        return output

    @agent
    def repository_cloner(self) -> Agent:
        """Agent responsible for cloning GitHub repositories."""
        return Agent(
            config=self.agents_config['repository_cloner'],
            tools=[CloneGitHubRepoTool()],
            verbose=True
        )

    @agent
    def static_analyzer(self) -> Agent:
        """Agent responsible for static code analysis."""
        return Agent(
            config=self.agents_config['static_analyzer'],
            tools=[PMDStaticCodeAnalysisTool()],
            verbose=True
        )

    @agent
    def dependency_scanner(self) -> Agent:
        """Agent responsible for scanning dependencies for vulnerabilities."""
        return Agent(
            config=self.agents_config['dependency_scanner'],
            tools=[DependencyVulnScanTool()],
            verbose=True
        )

    @agent
    def secret_detector(self) -> Agent:
        """Agent responsible for detecting hardcoded secrets."""
        return Agent(
            config=self.agents_config['secret_detector'],
            tools=[SecretDetectionTool()],
            verbose=True
        )

    @agent
    def secret_remediator(self) -> Agent:
        """Agent responsible for fixing hardcoded secrets."""
        return Agent(
            config=self.agents_config['secret_remediator'],
            tools=[FileReadTool(), FileWriterTool()],
            verbose=True
        )

    @agent
    def remediation_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['remediation_engineer'],
            tools=[FixSingleFileTool(), CommitChangesTool()],
            verbose=True
        )

    @task
    def clone_repository_task(self) -> Task:
        """Task to clone a GitHub repository."""
        return Task(
            config=self.tasks_config['clone_repository_task'],
        )

    @task
    def run_static_analysis_task(self) -> Task:
        """Task to run static code analysis."""
        return Task(
            config=self.tasks_config['run_static_analysis_task'],
            output_json=FilesToFix
        )

    @task
    @listen("run_static_analysis_task")
    def fix_static_code(self) -> Task:
        """Task to fix static code."""
        return Task(
            config=self.tasks_config['fix_static_code'],
        )

    @task
    @listen("run_static_analysis_task")
    def commit_changes(self) -> Task:
        """Task to commit changes made."""
        return Task(
            config=self.tasks_config['commit_changes'],
        )

    # @task
    # def scan_dependencies_task(self) -> Task:
    #     """Task to scan dependencies for vulnerabilities."""
    #     return Task(
    #         config=self.tasks_config['scan_dependencies_task'],
    #     )

    # @task
    # def detect_secrets_task(self) -> Task:
    #     """Task to detect hardcoded secrets."""
    #     return Task(
    #         config=self.tasks_config['detect_secrets_task'],
    #     )

    # @task
    # def remediate_secrets_task(self) -> Task:
    #     """Task to remediate hardcoded secrets."""
    #     return Task(
    #         config=self.tasks_config['remediate_secrets_task'],
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the AppsecAgents crew."""
        return Crew(
            agents=self.agents,  # Automatically populated by the @agent decorator
            tasks=self.tasks,  # Automatically populated by the @task decorator
            process=Process.sequential,  # Run tasks sequentially
            verbose=True,
        )
