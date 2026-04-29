import io
import os
import re
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from ai_research_reporter.crew import AiResearchReporterCrew

load_dotenv()

try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    if "MODEL" in st.secrets:
        os.environ["MODEL"] = st.secrets["MODEL"]
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass


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


def generate_pdf_bytes(title: str, content: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))

    for line in content.split("\n"):
        clean_line = line.strip()
        if not clean_line:
            story.append(Spacer(1, 8))
        else:
            safe_line = (
                clean_line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            story.append(Paragraph(safe_line, styles["BodyText"]))
            story.append(Spacer(1, 6))

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


st.set_page_config(
    page_title="AI Research Report Generator",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Research Report Generator")
st.caption("CrewAI + Streamlit + PDF Export")

with st.sidebar:
    st.header("Quick Topics")
    quick_topics = [
        "How AI agents are transforming DevOps",
        "Future of CI/CD with AI",
        "Cybersecurity trends in 2026",
        "AI in healthcare diagnosis",
        "Top DevOps tools in 2026"
    ]

    for topic_option in quick_topics:
        if st.button(topic_option):
            st.session_state["selected_topic"] = topic_option

default_topic = st.session_state.get("selected_topic", "")
topic = st.text_input(
    "Enter your topic",
    value=default_topic,
    placeholder="Example: How AI agents are transforming DevOps"
)

if st.button("Generate Report", use_container_width=True):
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        try:
            with st.spinner("Generating report... Please wait."):
                inputs = {"topic": topic}
                result = AiResearchReporterCrew().crew().kickoff(inputs=inputs)
                report_text = str(result)

                saved_file = save_report(topic, report_text)
                pdf_bytes = generate_pdf_bytes(f"Report on {topic}", report_text)

            st.success("Report generated successfully.")
            st.subheader("Generated Report")
            st.markdown(report_text)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="Download Markdown",
                    data=report_text,
                    file_name=f"{make_safe_filename(topic)}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with col2:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"{make_safe_filename(topic)}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            st.info(f"Saved locally at: {saved_file}")

        except Exception as e:
            st.error(f"An error occurred: {e}")