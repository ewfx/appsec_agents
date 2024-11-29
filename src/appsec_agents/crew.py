from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

# Import custom tools for the project
from tools.git_pr_tool import GitPRTool
from tools.github_tool import CloneGitHubRepoTool
from tools.dependency_scanner import DependencyVulnerabilityScanTool
from tools.sca_tool import StaticCodeAnalysisTool
from tools.secret_tool import SecretDetectionTool

@CrewBase
class AppsecAgents():
    """AppsecAgents crew for identifying, diagnosing, and fixing security vulnerabilities."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @before_kickoff  # Hook to execute before the crew starts
    def setup_environment(self, inputs):
        """Prepare the environment or inputs before kickoff."""
        print("Setting up the environment for the security analysis crew...")
        inputs['repo_path'] = "/tmp/cloned_repo"  # Example of dynamically added input
        return inputs

    @after_kickoff  # Hook to execute after the crew finishes
    def summarize_results(self, output):
        """Log or summarize results after the crew finishes."""
        print(f"Security Analysis Results: {output}")
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
            tools=[StaticCodeAnalysisTool()],
            verbose=True
        )

    @agent
    def dependency_scanner(self) -> Agent:
        """Agent responsible for scanning dependencies for vulnerabilities."""
        return Agent(
            config=self.agents_config['dependency_scanner'],
            tools=[DependencyVulnerabilityScanTool()],
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
    def remediation_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['remediation_engineer'],
            tools=[GitPRTool()],  # Add the custom tool for submitting PRs
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
        )

    @task
    def scan_dependencies_task(self) -> Task:
        """Task to scan dependencies for vulnerabilities."""
        return Task(
            config=self.tasks_config['scan_dependencies_task'],
        )

    @task
    def detect_secrets_task(self) -> Task:
        """Task to detect hardcoded secrets."""
        return Task(
            config=self.tasks_config['detect_secrets_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AppsecAgents crew."""
        return Crew(
            agents=self.agents,  # Automatically populated by the @agent decorator
            tasks=self.tasks,  # Automatically populated by the @task decorator
            process=Process.sequential,  # Run tasks sequentially
            verbose=True,
        )
