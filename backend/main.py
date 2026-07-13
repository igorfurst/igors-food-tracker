import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from daily_log_service import compute_daily_log

app = FastAPI(title="Igor's Food Tracker API")

DATA_DIR = Path(__file__).parent / "data"
FOODS_FILE = DATA_DIR / "foods.json"
MEALS_FILE = DATA_DIR / "meals.json"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LogEntry(BaseModel):
    type: str
    key: str
    quantity: float = 1


class DailyLogRequest(BaseModel):
    entries: list[LogEntry]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/meals")
def meals():
    return json.loads(MEALS_FILE.read_text(encoding="utf-8"))


@app.get("/foods")
def foods():
    return json.loads(FOODS_FILE.read_text(encoding="utf-8"))


@app.post("/daily-log")
def daily_log(payload: DailyLogRequest):
    entries = [entry.model_dump() for entry in payload.entries]
    return compute_daily_log(entries)
