import json
import sys
from datetime import date

from garmin_service import get_daily_calories_burned
from nutrition_service import DATA_DIR, NUTRIENT_KEYS

FOODS_FILE = DATA_DIR / "foods.json"
MEALS_FILE = DATA_DIR / "meals.json"
GARMIN_CACHE_FILE = DATA_DIR / "garmin-cache.json"


def _load_json(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _add_scaled(totals, source, quantity):
    for key in NUTRIENT_KEYS:
        value = source[key]
        if value is not None:
            totals[key] = round((totals[key] or 0) + value * quantity, 3)


def compute_intake(entries):
    foods = _load_json(FOODS_FILE)
    meals = _load_json(MEALS_FILE)
    totals = {k: None for k in NUTRIENT_KEYS}

    for entry in entries:
        key = entry["key"]
        quantity = entry.get("quantity", 1)
        if entry["type"] == "food":
            food = foods[key]
            scale = quantity if food["unit"] == "1 kos" else quantity / 100
            _add_scaled(totals, food, scale)
        elif entry["type"] == "meal":
            _add_scaled(totals, meals[key], quantity)

    return totals


def get_garmin_today():
    try:
        return get_daily_calories_burned()
    except Exception as e:
        print(f"Garmin fetch failed, falling back to cache: {e}", file=sys.stderr)
        cache = _load_json(GARMIN_CACHE_FILE)
        return cache.get(date.today().isoformat())


def compute_daily_log(entries):
    intake = compute_intake(entries)
    garmin = get_garmin_today()
    balance = None
    if intake["calories"] is not None and garmin and garmin.get("total_calories") is not None:
        balance = round(intake["calories"] - garmin["total_calories"], 1)
    return {"intake": intake, "garmin": garmin, "balance": balance}
