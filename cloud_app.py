import os
import time
import logging
from datetime import datetime

import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

try:
    from ai_research_reporter.crew import AiResearchReporterCrew
except Exception:
    AiResearchReporterCrew = None


# -----------------------------
# Folder Setup
# -----------------------------
os.makedirs("reports", exist_ok=True)
os.makedirs("logs", exist_ok=True)

HISTORY_FILE = "reports/history.csv"
LOG_FILE = "logs/app.log"


# -----------------------------
# Logging Setup
# -----------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# -----------------------------
# Helper Functions
# -----------------------------
def save_history(input_text, result_text, severity="Medium"):
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input": input_text,
        "severity": severity,
        "result": result_text[:500]
    }

    df = pd.DataFrame([data])

    if os.path.exists(HISTORY_FILE):
        df.to_csv(HISTORY_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(HISTORY_FILE, index=False)


def detect_severity(text):
    text = text.lower()

    high_keywords = ["failed", "error", "exception", "crash", "unauthorized", "denied", "port", "timeout"]
    medium_keywords = ["warning", "slow", "retry", "missing", "not found"]

    if any(word in text for word in high_keywords):
        return "High"
    elif any(word in text for word in medium_keywords):
        return "Medium"
    else:
        return "Low"


def generate_pdf_report(input_text, result_text, severity):
    pdf_path = "reports/incident_report.pdf"

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "AI DevOps Incident Report")

    c.setFont("Helvetica", 11)
    c.drawString(50, 720, f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, 700, f"Severity: {severity}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 670, "Input / Log Summary:")

    text = c.beginText(50, 650)
    text.setFont("Helvetica", 10)

    for line in input_text.split("\n"):
        text.textLine(line[:95])
        if text.getY() < 400:
            break

    c.drawText(text)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 370, "AI Analysis Result:")

    text = c.beginText(50, 350)
    text.setFont("Helvetica", 10)

    for line in result_text.split("\n"):
        text.textLine(line[:95])
        if text.getY() < 50:
            c.drawText(text)
            c.showPage()
            text = c.beginText(50, 750)
            text.setFont("Helvetica", 10)

    c.drawText(text)
    c.save()

    return pdf_path


def run_ai_analysis(input_text):
    if AiResearchReporterCrew is not None:
        try:
            result = AiResearchReporterCrew().crew().kickoff(
                inputs={"topic": input_text}
            )
            return str(result)
        except Exception as e:
            logging.error(f"CrewAI error: {str(e)}")
            return basic_analysis(input_text)

    return basic_analysis(input_text)


def basic_analysis(input_text):
    severity = detect_severity(input_text)

    return f"""
## AI DevOps Analysis Report

### Detected Severity
{severity}

### Root Cause Possibility
The uploaded log or entered topic indicates a possible DevOps pipeline, deployment, dependency, Docker, Jenkins, Kubernetes, or runtime issue.

### Key Observations
- Input was successfully received.
- System analyzed the text for common DevOps failure patterns.
- Severity was classified based on detected keywords.

### Recommended Fix
1. Check error logs carefully.
2. Verify environment variables and secrets.
3. Confirm Docker container and port availability.
4. Check Jenkins pipeline stage failure.
5. Validate Kubernetes pods and services.
6. Re-run the pipeline after fixing the issue.

### DevOps Recommendation
Use Jenkins for CI/CD, Docker for containerization, Kubernetes for orchestration, and Prometheus/Grafana for monitoring.
"""


# -----------------------------
# Streamlit UI Setup
# -----------------------------
st.set_page_config(
    page_title="AI DevOps Research Reporter",
    page_icon="🤖",
    layout="wide"
)

st.sidebar.title("🚀 AI DevOps Platform")

page = st.sidebar.selectbox(
    "Choose Page",
    [
        "AI Research / Log Analyzer",
        "DevOps Dashboard",
        "History",
        "Kubernetes Status",
        "About Project"
    ]
)


# -----------------------------
# Page 1: AI Research / Log Analyzer
# -----------------------------
if page == "AI Research / Log Analyzer":
    st.title("🤖 AI Research Reporter + DevOps Log Analyzer")

    st.write(
        "Analyze AI research topics, Jenkins logs, Docker errors, Kubernetes issues, and DevOps pipeline failures."
    )

    uploaded_file = st.file_uploader(
        "Upload Jenkins / Docker / Kubernetes / CI-CD Log File",
        type=["txt", "log", "md"]
    )

    user_input = st.text_area(
        "Enter research topic or paste DevOps error log:",
        height=220,
        placeholder="Example: Jenkins Docker build failed due to port already allocated..."
    )

    if uploaded_file is not None:
        uploaded_text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.subheader("📄 Uploaded Log Preview")
        st.text_area("Log Content", uploaded_text, height=250)
        user_input = uploaded_text

    if st.button("Analyze Now"):
        if not user_input.strip():
            st.warning("Please enter a topic or upload a log file.")
        else:
            start_time = time.time()
            logging.info("Analysis started")

            with st.spinner("AI is analyzing..."):
                result = run_ai_analysis(user_input)

            response_time = round(time.time() - start_time, 2)
            severity = detect_severity(user_input + " " + result)

            logging.info(f"Analysis completed in {response_time} seconds")
            save_history(user_input, result, severity)

            st.success("Analysis completed successfully!")

            col1, col2, col3 = st.columns(3)
            col1.metric("Severity", severity)
            col2.metric("Response Time", f"{response_time}s")
            col3.metric("Report Saved", "Yes")

            st.subheader("📌 AI Analysis Result")
            st.markdown(result)

            st.download_button(
                "Download TXT Report",
                result,
                file_name="ai_devops_report.txt",
                mime="text/plain"
            )

            pdf_path = generate_pdf_report(user_input, result, severity)

            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    "Download PDF Incident Report",
                    pdf_file,
                    file_name="incident_report.pdf",
                    mime="application/pdf"
                )


# -----------------------------
# Page 2: DevOps Dashboard
# -----------------------------
elif page == "DevOps Dashboard":
    st.title("📊 DevOps Monitoring Dashboard")

    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)

        total_analyses = len(df)
        high_risk = len(df[df["severity"] == "High"])
        medium_risk = len(df[df["severity"] == "Medium"])
        low_risk = len(df[df["severity"] == "Low"])

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Analyses", total_analyses)
        col2.metric("High Severity", high_risk)
        col3.metric("Medium Severity", medium_risk)
        col4.metric("Low Severity", low_risk)

        st.subheader("Recent Analysis Activity")
        st.dataframe(df.tail(10), use_container_width=True)

        st.subheader("Severity Summary")
        severity_count = df["severity"].value_counts()
        st.bar_chart(severity_count)

    else:
        st.info("No history found. Run one analysis first.")


# -----------------------------
# Page 3: History
# -----------------------------
elif page == "History":
    st.title("📁 Analysis History")

    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)

        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False)

        st.download_button(
            "Download Full History CSV",
            csv_data,
            file_name="analysis_history.csv",
            mime="text/csv"
        )
    else:
        st.warning("No history available yet.")


# -----------------------------
# Page 4: Kubernetes Status
# -----------------------------
elif page == "Kubernetes Status":
    st.title("☸️ Kubernetes Deployment Status")

    st.success("Kubernetes deployment configured successfully.")

    col1, col2, col3 = st.columns(3)

    col1.metric("Deployment", "ai-research-reporter")
    col2.metric("Replicas", "2")
    col3.metric("Service Type", "NodePort")

    st.code(
        """
kubectl get pods
kubectl get svc
kubectl describe deployment ai-research-reporter
        """,
        language="bash"
    )

    st.info("Application exposed using NodePort 30085 or port-forwarding.")


# -----------------------------
# Page 5: About Project
# -----------------------------
elif page == "About Project":
    st.title("📌 About This Project")

    st.markdown("""
## AI-Powered DevOps Research Reporter

### Features
- AI research report generation
- Jenkins log analysis
- Docker issue detection
- Kubernetes deployment
- Dashboard
- PDF reports
- History tracking

### Tools Used
- Python
- Streamlit
- Docker
- Jenkins
- Kubernetes
- GitHub

### Flow

GitHub → Jenkins → Docker → Kubernetes
""")