from ai_research_reporter.crew import AiResearchReporterCrew
from datetime import datetime
import re


def make_safe_filename(text: str) -> str:
    """
    Convert topic text into a safe filename.
    Example: 'AI in Healthcare' -> 'AI_in_Healthcare'
    """
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9_\-]", "", text)
    return text[:50] if text else "report"


def save_report(topic: str, content: str) -> str:
    """
    Save final report to a markdown file with topic + timestamp.
    """
    safe_topic = make_safe_filename(topic)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"# Report on {topic}\n\n")
        file.write(content)

    return filename


def run():
    try:
        print("\n=== AI Research Report Generator ===\n")

        topic = input("Enter your topic: ").strip()

        if not topic:
            topic = "Artificial Intelligence in Healthcare"
            print(f"\nNo topic entered. Using default topic: {topic}\n")

        inputs = {
            "topic": topic
        }

        print(f"Generating report for topic: {topic}\n")

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