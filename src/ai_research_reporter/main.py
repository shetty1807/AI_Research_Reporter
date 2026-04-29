from ai_research_reporter.crew import AiResearchReporterCrew
from datetime import datetime
import re
import os


def make_safe_filename(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9_\-]", "", text)
    return text[:60] if text else "report"


def save_report(topic: str, content: str) -> str:
    reports_folder = "reports"
    os.makedirs(reports_folder, exist_ok=True)

    safe_topic = make_safe_filename(topic)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.md"
    filepath = os.path.join(reports_folder, filename)

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(f"# Report on {topic}\n\n")
        file.write(content)

    return filepath


def run():
    try:
        print("\n=== AI Research Report Generator ===\n")

        topic = input("Enter your topic: ").strip()

        if not topic:
            topic = "How AI agents are transforming DevOps"
            print(f"\nNo topic entered. Using default topic: {topic}\n")

        inputs = {"topic": topic}

        result = AiResearchReporterCrew().crew().kickoff(inputs=inputs)
        final_output = str(result)

        print("\n" + "=" * 60)
        print("FINAL OUTPUT")
        print("=" * 60)
        print(final_output)
        print("=" * 60)

        saved_file = save_report(topic, final_output)
        print(f"\nReport saved successfully as: {saved_file}\n")

    except Exception as e:
        print(f"\nAn error occurred while running the crew: {e}\n")


if __name__ == "__main__":
    run()