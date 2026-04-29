from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import os
import re

from ai_research_reporter.crew import AiResearchReporterCrew

app = FastAPI(
    title="AI DevOps Pipeline Failure Analyzer",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DevOpsRequest(BaseModel):
    platform: str = Field(..., min_length=2)
    status: str = Field(..., min_length=2)
    logs: str = Field(..., min_length=10)


def make_safe_filename(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9_\-]", "", text)
    return text[:60] if text else "incident_report"


def save_report(platform: str, content: str) -> str:
    reports_folder = "reports"
    os.makedirs(reports_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{make_safe_filename(platform)}_incident_{timestamp}.md"
    filepath = os.path.join(reports_folder, filename)

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)

    return filepath


@app.get("/")
def home():
    return {
        "message": "AI DevOps Pipeline Failure Analyzer API is running"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze-pipeline")
def analyze_pipeline(request: DevOpsRequest):
    try:
        inputs = {
            "platform": request.platform,
            "status": request.status,
            "logs": request.logs
        }

        result = AiResearchReporterCrew().crew().kickoff(inputs=inputs)
        final_output = str(result)

        saved_file = save_report(request.platform, final_output)

        return {
            "success": True,
            "platform": request.platform,
            "status": request.status,
            "report": final_output,
            "saved_file": saved_file,
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))