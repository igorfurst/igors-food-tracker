import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Igor's Food Tracker API")

MEALS_FILE = Path(__file__).parent / "data" / "meals.json"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/meals")
def meals():
    return json.loads(MEALS_FILE.read_text(encoding="utf-8"))
