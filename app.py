import io
import requests
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

API_BASE_URL = "http://127.0.0.1:8000"


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


def fetch_report_history():
    try:
        response = requests.get(f"{API_BASE_URL}/reports", timeout=30)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


st.set_page_config(
    page_title="AI Research Report Generator",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Research Report Generator")
st.caption("CrewAI + FastAPI + Streamlit + PDF Export")

with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API Base URL", value=API_BASE_URL)
    API_BASE_URL = api_url.strip() or API_BASE_URL

    st.markdown("---")
    st.subheader("Quick Topics")
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

    st.markdown("---")
    st.subheader("Report History")
    history = fetch_report_history()

    if history:
        for item in history[:10]:
            st.markdown(f"**{item['filename']}**")
            st.caption(item["created_at"])
    else:
        st.caption("No report history found yet.")

default_topic = st.session_state.get("selected_topic", "")
topic = st.text_input(
    "Enter your topic",
    value=default_topic,
    placeholder="Example: How AI agents are transforming DevOps"
)

col1, col2 = st.columns([1, 1])

with col1:
    generate_clicked = st.button("Generate Report", use_container_width=True)

with col2:
    health_clicked = st.button("Check API Health", use_container_width=True)

if health_clicked:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            st.success("API is running successfully.")
        else:
            st.error("API responded, but not successfully.")
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

if generate_clicked:
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        try:
            with st.spinner("Generating report... Please wait."):
                response = requests.post(
                    f"{API_BASE_URL}/generate-report",
                    json={"topic": topic},
                    timeout=300
                )

            if response.status_code == 200:
                data = response.json()
                report_text = data["report"]
                saved_file = data["saved_file"]

                st.success("Report generated successfully.")

                st.subheader("Generated Report")
                st.markdown(report_text)

                md_filename = topic.strip().replace(" ", "_") + ".md"
                pdf_filename = topic.strip().replace(" ", "_") + ".pdf"

                pdf_bytes = generate_pdf_bytes(f"Report on {topic}", report_text)

                dcol1, dcol2 = st.columns(2)

                with dcol1:
                    st.download_button(
                        label="Download Markdown",
                        data=report_text,
                        file_name=md_filename,
                        mime="text/markdown",
                        use_container_width=True
                    )

                with dcol2:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )

                st.info(f"Saved locally at: {saved_file}")

            else:
                try:
                    error_data = response.json()
                    st.error(f"API Error: {error_data}")
                except Exception:
                    st.error(f"API Error: {response.text}")

        except Exception as e:
            st.error(f"An error occurred: {e}")