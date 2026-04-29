import os
import io
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


def extract_field(report_text: str, field_name: str) -> str:
    lines = report_text.splitlines()
    field_name_lower = field_name.lower()

    for i, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped.startswith(f"## {field_name_lower}") or stripped.startswith(f"**{field_name_lower}**"):
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line:
                    return next_line

        if stripped.startswith(f"{field_name_lower}:") or stripped.startswith(f"**{field_name_lower}:"):
            parts = line.split(":", 1)
            if len(parts) > 1:
                return parts[1].strip().replace("*", "")

    return "Not clearly identified"


st.set_page_config(
    page_title="AI DevOps Pipeline Failure Analyzer",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ AI DevOps Pipeline Failure Analyzer")
st.caption("CrewAI + Streamlit + Severity + Issue Category")

with st.sidebar:
    st.header("Quick Error Examples")

    examples = {
        "Jenkins Missing Dependency": {
            "platform": "Jenkins",
            "status": "Build Error",
            "logs": "ModuleNotFoundError: No module named requests"
        },
        "GitHub Actions YAML Error": {
            "platform": "GitHub Actions",
            "status": "Build Error",
            "logs": "YAML syntax error on line 14: mapping values are not allowed here"
        },
        "GitLab Unauthorized API": {
            "platform": "GitLab CI",
            "status": "Failed",
            "logs": "401 Unauthorized while calling TestNeo API"
        },
        "Docker Build Failure": {
            "platform": "Jenkins",
            "status": "Build Error",
            "logs": "docker build failed: failed to read dockerfile: no such file or directory"
        }
    }

    for label, value in examples.items():
        if st.button(label, use_container_width=True):
            st.session_state["platform"] = value["platform"]
            st.session_state["status"] = value["status"]
            st.session_state["logs"] = value["logs"]

platform_options = [
    "Jenkins",
    "GitHub Actions",
    "GitLab CI",
    "Bitbucket Pipelines",
    "CircleCI",
    "Other"
]
status_options = [
    "Failed",
    "Passed with Warnings",
    "Deployment Error",
    "Build Error",
    "Test Failure"
]

platform = st.selectbox(
    "Select CI/CD Platform",
    platform_options,
    index=platform_options.index(st.session_state.get("platform", "Jenkins"))
)

status = st.selectbox(
    "Pipeline Status",
    status_options,
    index=status_options.index(st.session_state.get("status", "Failed"))
)

logs = st.text_area(
    "Paste pipeline logs or error output",
    height=250,
    value=st.session_state.get("logs", ""),
    placeholder="Example: ModuleNotFoundError: No module named requests"
)

if st.button("Analyze Pipeline Failure", use_container_width=True):
    if not logs.strip():
        st.warning("Please paste pipeline logs or error output.")
    else:
        try:
            with st.spinner("Analyzing pipeline logs... Please wait."):
                inputs = {
                    "platform": platform,
                    "status": status,
                    "logs": logs
                }

                result = AiResearchReporterCrew().crew().kickoff(inputs=inputs)
                report_text = str(result)
                pdf_bytes = generate_pdf_bytes(f"{platform} Incident Report", report_text)

            st.success("Pipeline analysis completed successfully.")

            issue_category = extract_field(report_text, "Issue Category")
            severity = extract_field(report_text, "Severity")
            root_cause = extract_field(report_text, "Root Cause")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.info(f"**Issue Category:** {issue_category}")
            with c2:
                st.warning(f"**Severity:** {severity}")
            with c3:
                st.success(f"**Platform:** {platform}")

            st.subheader("Root Cause")
            st.write(root_cause)

            st.subheader("Incident Report")
            st.markdown(report_text)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="Download Markdown",
                    data=report_text,
                    file_name=f"{platform.lower().replace(' ', '_')}_incident_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with col2:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"{platform.lower().replace(' ', '_')}_incident_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"An error occurred: {e}")