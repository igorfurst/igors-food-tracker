import json
import os
import re
from pathlib import Path

import requests

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
OFF_BARCODE_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

DATA_DIR = Path(__file__).parent / "data"
FOODS_FILE = DATA_DIR / "foods.json"

HEADERS = {"User-Agent": "IgorsFoodTracker/1.0 (igorfurst@gmail.com)"}


def _slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug


def _save_food(key, entry):
    if FOODS_FILE.exists():
        data = json.loads(FOODS_FILE.read_text(encoding="utf-8"))
    else:
        data = {}
    data[key] = entry
    FOODS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _find_usda_nutrient(nutrients, name, unit=None):
    matches = [n for n in nutrients if name.lower() in n.get("nutrientName", "").lower()]
    if unit:
        for m in matches:
            if m.get("unitName", "").upper() == unit.upper():
                return m.get("value")
    return matches[0].get("value") if matches else None


def fetch_from_usda(query, label=None):
    api_key = os.environ["USDA_API_KEY"]
    response = requests.get(
        USDA_SEARCH_URL,
        params={"query": query, "api_key": api_key, "pageSize": 1},
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    foods = response.json().get("foods", [])
    if not foods:
        raise ValueError(f"No USDA results for query: {query}")
    food = foods[0]
    nutrients = food.get("foodNutrients", [])

    calories = _find_usda_nutrient(nutrients, "Energy", "KCAL")
    protein = _find_usda_nutrient(nutrients, "Protein", "G")
    fat = _find_usda_nutrient(nutrients, "Total lipid (fat)", "G")
    b12 = _find_usda_nutrient(nutrients, "Vitamin B-12", "UG")
    vitamin_d = _find_usda_nutrient(nutrients, "Vitamin D", "UG")
    carbs = _find_usda_nutrient(nutrients, "Carbohydrate, by difference", "G")
    fiber = _find_usda_nutrient(nutrients, "Fiber, total dietary", "G")
    sugar = _find_usda_nutrient(nutrients, "Sugars, total", "G")
    sodium = _find_usda_nutrient(nutrients, "Sodium, Na", "MG")

    entry = {
        "name": food.get("description", query),
        "calories": calories,
        "protein_g": protein,
        "fat_g": fat,
    }
    if b12 is not None:
        entry["vitamin_b12"] = f"{b12} µg"
    if vitamin_d is not None:
        entry["vitamin_d"] = f"{vitamin_d} µg"
    if carbs is not None:
        entry["carbs_g"] = carbs
    if fiber is not None:
        entry["fiber_g"] = fiber
    if sugar is not None:
        entry["sugar_g"] = sugar
    if sodium is not None:
        entry["sodium_mg"] = sodium

    key = label or _slugify(query)
    _save_food(key, entry)
    return entry


def fetch_from_openfoodfacts(barcode_or_query, label=None):
    if barcode_or_query.isdigit():
        response = requests.get(
            OFF_BARCODE_URL.format(barcode=barcode_or_query), headers=HEADERS, timeout=10
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != 1:
            raise ValueError(f"No OpenFoodFacts product for barcode: {barcode_or_query}")
        product = payload["product"]
    else:
        response = requests.get(
            OFF_SEARCH_URL,
            params={
                "search_terms": barcode_or_query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 1,
            },
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        products = response.json().get("products", [])
        if not products:
            raise ValueError(f"No OpenFoodFacts results for query: {barcode_or_query}")
        product = products[0]

    nutriments = product.get("nutriments", {})

    def unit_of(field, default="g"):
        return nutriments.get(f"{field}_unit", default)

    entry = {
        "name": product.get("product_name") or barcode_or_query,
        "calories": nutriments.get("energy-kcal_100g"),
        "protein_g": nutriments.get("proteins_100g"),
        "fat_g": nutriments.get("fat_100g"),
    }
    b12 = nutriments.get("vitamin-b12_100g")
    if b12 is not None:
        entry["vitamin_b12"] = f"{b12} {unit_of('vitamin-b12', 'µg')}"
    vitamin_d = nutriments.get("vitamin-d_100g")
    if vitamin_d is not None:
        entry["vitamin_d"] = f"{vitamin_d} {unit_of('vitamin-d', 'µg')}"
    carbs = nutriments.get("carbohydrates_100g")
    if carbs is not None:
        entry["carbs_g"] = carbs
    fiber = nutriments.get("fiber_100g")
    if fiber is not None:
        entry["fiber_g"] = fiber
    sugar = nutriments.get("sugars_100g")
    if sugar is not None:
        entry["sugar_g"] = sugar
    sodium = nutriments.get("sodium_100g")
    if sodium is not None:
        entry["sodium_mg"] = sodium * 1000

    key = label or _slugify(barcode_or_query)
    _save_food(key, entry)
    return entry
