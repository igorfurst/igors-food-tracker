import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
CACHE_FILE = DATA_DIR / "garmin-cache.json"
TOKEN_STORE = DATA_DIR / ".garmin_tokens"

DEFAULT_MAX_AGE_HOURS = 12


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


def _is_stale(entry, max_age_hours):
    fetched_at = entry.get("fetched_at")
    if not fetched_at:
        return True
    age = datetime.now(timezone.utc) - datetime.fromisoformat(fetched_at)
    return age.total_seconds() > max_age_hours * 3600


def get_daily_calories_burned(day=None, max_age_hours=DEFAULT_MAX_AGE_HOURS, force_refresh=False):
    day = day or date.today()
    key = day.isoformat()
    cache = _load_cache()
    entry = cache.get(key)

    if not force_refresh and entry and not _is_stale(entry, max_age_hours):
        return entry

    calories = _fetch_calories_from_garmin(day)
    calories["fetched_at"] = datetime.now(timezone.utc).isoformat()
    cache[key] = calories
    _save_cache(cache)
    return calories


if __name__ == "__main__":
    print(get_daily_calories_burned())
