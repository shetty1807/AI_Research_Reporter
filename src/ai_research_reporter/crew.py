from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class AiResearchReporterCrew:
    """DevOps Pipeline Failure Analyzer Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def log_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["log_analyst"],
            verbose=True
        )

    @agent
    def root_cause_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["root_cause_expert"],
            verbose=True
        )

    @agent
    def fix_recommender(self) -> Agent:
        return Agent(
            config=self.agents_config["fix_recommender"],
            verbose=True
        )

    @agent
    def incident_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["incident_writer"],
            verbose=True
        )

    @task
    def log_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["log_analysis_task"]
        )

    @task
    def root_cause_task(self) -> Task:
        return Task(
            config=self.tasks_config["root_cause_task"]
        )

    @task
    def fix_recommendation_task(self) -> Task:
        return Task(
            config=self.tasks_config["fix_recommendation_task"]
        )

    @task
    def incident_report_task(self) -> Task:
        return Task(
            config=self.tasks_config["incident_report_task"]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )