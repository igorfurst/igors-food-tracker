import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from daily_log_service import compute_daily_log
from nutrition_service import _slugify, fetch_from_openfoodfacts, fetch_from_usda

app = FastAPI(title="Igor's Food Tracker API")

DATA_DIR = Path(__file__).parent / "data"
FOODS_FILE = DATA_DIR / "foods.json"
MEALS_FILE = DATA_DIR / "meals.json"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://silly-tulumba-1c04b6.netlify.app",
    ],
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


class FoodLookupRequest(BaseModel):
    name: str


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


@app.post("/foods/lookup")
def foods_lookup(payload: FoodLookupRequest):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Ime živila ne sme biti prazno.")

    try:
        entry = fetch_from_usda(name, name=name)
    except Exception:
        try:
            entry = fetch_from_openfoodfacts(name, name=name)
        except Exception:
            raise HTTPException(
                status_code=404,
                detail=f"Živila '{name}' ni bilo mogoče najti niti v USDA niti v Open Food Facts.",
            )

    return {"key": _slugify(name), **entry}
