from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from datetime import datetime
import os
import re
from typing import List

from ai_research_reporter.crew import AiResearchReporterCrew

app = FastAPI(
    title="AI Research Report Generator API",
    description="FastAPI backend for CrewAI research report generation",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReportRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Topic for report generation")


class ReportResponse(BaseModel):
    success: bool
    topic: str
    report: str
    saved_file: str
    generated_at: str


class ReportHistoryItem(BaseModel):
    filename: str
    filepath: str
    created_at: str


REPORTS_FOLDER = "reports"


def make_safe_filename(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9_\-]", "", text)
    return text[:60] if text else "report"


def ensure_reports_folder() -> None:
    os.makedirs(REPORTS_FOLDER, exist_ok=True)


def save_report(topic: str, content: str) -> str:
    ensure_reports_folder()
    safe_topic = make_safe_filename(topic)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.md"
    filepath = os.path.join(REPORTS_FOLDER, filename)

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(f"# Report on {topic}\n\n")
        file.write(content)

    return filepath


def list_reports() -> List[ReportHistoryItem]:
    ensure_reports_folder()
    files = []

    for filename in os.listdir(REPORTS_FOLDER):
        if filename.endswith(".md"):
            filepath = os.path.join(REPORTS_FOLDER, filename)
            created_ts = os.path.getctime(filepath)
            created_at = datetime.fromtimestamp(created_ts).strftime("%Y-%m-%d %H:%M:%S")
            files.append(
                ReportHistoryItem(
                    filename=filename,
                    filepath=filepath,
                    created_at=created_at
                )
            )

    files.sort(key=lambda x: x.created_at, reverse=True)
    return files


@app.get("/")
def home():
    return {
        "message": "AI Research Report Generator API is running",
        "docs_url": "/docs",
        "health_url": "/health",
        "history_url": "/reports"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/generate-report", response_model=ReportResponse)
def generate_report(request: ReportRequest):
    try:
        topic = request.topic.strip()
        inputs = {"topic": topic}

        result = AiResearchReporterCrew().crew().kickoff(inputs=inputs)
        final_output = str(result)

        saved_file = save_report(topic, final_output)

        return ReportResponse(
            success=True,
            topic=topic,
            report=final_output,
            saved_file=saved_file,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@app.get("/reports", response_model=List[ReportHistoryItem])
def get_reports():
    try:
        return list_reports()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/{filename}")
def download_report(filename: str):
    filepath = os.path.join(REPORTS_FOLDER, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path=filepath,
        media_type="text/markdown",
        filename=filename
    )