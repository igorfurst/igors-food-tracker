import json
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
CACHE_FILE = DATA_DIR / "garmin-cache.json"
TOKEN_STORE = DATA_DIR / ".garmin_tokens"


def _load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _fetch_calories_from_garmin(day):
    client = Garmin(os.environ["GARMIN_EMAIL"], os.environ["GARMIN_PASSWORD"])
    client.login(tokenstore=str(TOKEN_STORE))
    summary = client.get_stats(day.isoformat())
    return {
        "total_calories": summary.get("totalKilocalories"),
        "active_calories": summary.get("activeKilocalories"),
        "bmr_calories": summary.get("bmrKilocalories"),
    }


def get_daily_calories_burned(day=None, force_refresh=False):
    day = day or date.today()
    key = day.isoformat()
    cache = _load_cache()

    if not force_refresh and key in cache:
        return cache[key]

    calories = _fetch_calories_from_garmin(day)
    cache[key] = calories
    _save_cache(cache)
    return calories


if __name__ == "__main__":
    print(get_daily_calories_burned())
