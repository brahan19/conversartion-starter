"""
Networking research crew: hierarchical CrewAI crew that takes a LinkedIn URL
and produces pointed questions and conversation starters using research,
personal context, critique, and a question architect.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env not loaded if python-dotenv not installed

from crewai import Crew, Process, LLM
from agents import create_agents
from tasks import create_tasks

# Ensure required keys are present (at least for the LLM)
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY not set. Set it in .env for the crew to run.")


def run_crew(linkedin_url):
    """
    Run the hierarchical crew with the given LinkedIn profile URL.
    Returns the crew's output (final task result).
    The Orchestrator is used as the manager; its loop is capped at 4 iterations per task.
    """
    agents = create_agents()
    task_list = create_tasks(agents, linkedin_url)

    # Orchestrator is the manager; it must not be in the agents list (CrewAI requirement).
    worker_agents = [
        agents["web_researcher"],
        agents["personal_context_agent"],
        agents["review_critique_agent"],
        agents["question_architect"],
    ]

    cheap_llm = LLM(model="gpt-4o-mini")
    # Manager agent is not in crew.agents, so it does not get crew's default LLM; set it explicitly.
    agents["orchestrator"].llm = cheap_llm
    crew = Crew(
        agents=worker_agents,
        tasks=task_list,
        process=Process.hierarchical,
        llm=cheap_llm,
        manager_agent=agents["orchestrator"],
        memory=True,
        verbose=True,
    )

    result = crew.kickoff()
    return result


if __name__ == "__main__":
    import re
    import sys
    from datetime import datetime

    if len(sys.argv) < 2:
        print("Usage: python main.py <linkedin_url>")
        print("Example: python main.py 'https://www.linkedin.com/in/williamhgates/'")
        sys.exit(1)

    url = sys.argv[1].strip()
    print("Running crew for LinkedIn URL: {}\n".format(url))
    output = run_crew(url)
    print("\n--- Crew output ---\n")
    result_str = str(output) if output is not None else ""
    print(result_str)

    # Save report in reports/ folder: {person_name}_{timestamp}.md
    person_slug = re.sub(r"[^a-zA-Z0-9]+", "_", url.strip("/").split("/")[-1] or "report")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_filename = "{}_{}.md".format(person_slug, timestamp)
    report_path = os.path.join(report_dir, report_filename)
    if result_str.strip():
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(result_str)
        print("\nReport saved to {}".format(report_path))
