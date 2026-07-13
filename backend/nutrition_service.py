import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_FOOD_URL = "https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
OFF_BARCODE_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

DATA_DIR = Path(__file__).parent / "data"
FOODS_FILE = DATA_DIR / "foods.json"

HEADERS = {"User-Agent": "IgorsFoodTracker/1.0 (igorfurst@gmail.com)"}

SI_TRANSLIT = str.maketrans("čšžČŠŽ", "cszCSZ")

UNIT_TO_GRAMS = {"g": 1, "mg": 1e-3, "µg": 1e-6, "mcg": 1e-6, "kg": 1000}

NUTRIENT_KEYS = [
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
    "iron_mg",
    "vitamin_b12_µg",
    "vitamin_d_µg",
    "omega_3_g",
]


def _slugify(text):
    text = text.translate(SI_TRANSLIT)
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _round(value):
    return None if value is None else round(value, 3)


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
        return None
    return matches[0].get("value") if matches else None


EXCLUDED_PORTION_WORDS = (
    "cup",
    "tablespoon",
    "teaspoon",
    "oz",
    "not specified",
    "slice",
    "wedge",
    "piece",
    "stick",
    "half",
    "chunk",
    "spear",
    "floret",
    "ring",
)


def _usda_piece_gram_weight(fdc_id, api_key):
    response = requests.get(
        USDA_FOOD_URL.format(fdc_id=fdc_id),
        params={"api_key": api_key},
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    portions = response.json().get("foodPortions", [])
    candidates = [
        p
        for p in portions
        if p.get("gramWeight")
        and (
            (p.get("amount") == 1)
            or (
                p.get("portionDescription", "").strip().lower().startswith("1 ")
                and not any(w in p.get("portionDescription", "").lower() for w in EXCLUDED_PORTION_WORDS)
            )
        )
    ]
    candidates = [c for c in candidates if 10 <= c["gramWeight"] <= 500]
    return candidates[0]["gramWeight"] if candidates else None


def fetch_from_usda(query, label=None, name=None, unit="100g"):
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

    values = {
        "calories": _find_usda_nutrient(nutrients, "Energy", "KCAL"),
        "protein_g": _find_usda_nutrient(nutrients, "Protein", "G"),
        "fat_g": _find_usda_nutrient(nutrients, "Total lipid (fat)", "G"),
        "carbs_g": _find_usda_nutrient(nutrients, "Carbohydrate, by difference", "G"),
        "iron_mg": _find_usda_nutrient(nutrients, "Iron, Fe", "MG"),
        "vitamin_b12_µg": _find_usda_nutrient(nutrients, "Vitamin B-12", "UG"),
        "vitamin_d_µg": _find_usda_nutrient(nutrients, "Vitamin D", "UG"),
        "omega_3_g": _find_usda_nutrient(nutrients, "omega-3", "G"),
    }

    actual_unit = "100g"
    if unit == "1 kos":
        gram_weight = _usda_piece_gram_weight(food["fdcId"], api_key)
        if gram_weight:
            scale = gram_weight / 100
            values = {k: (v * scale if v is not None else None) for k, v in values.items()}
            actual_unit = "1 kos"

    entry = {"name": name or food.get("description", query), "unit": actual_unit}
    entry.update({k: _round(v) for k, v in values.items()})

    key = label or _slugify(query)
    _save_food(key, entry)
    return entry


def _off_nutrient(nutriments, field, target_unit, default_unit):
    raw = nutriments.get(f"{field}_100g")
    if raw is None:
        return None
    source_unit = (nutriments.get(f"{field}_unit") or default_unit).lower()
    grams = raw * UNIT_TO_GRAMS.get(source_unit, 1)
    return grams / UNIT_TO_GRAMS[target_unit]


def fetch_from_openfoodfacts(barcode_or_query, label=None, name=None, unit="100g"):
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

    values = {
        "calories": nutriments.get("energy-kcal_100g"),
        "protein_g": _off_nutrient(nutriments, "proteins", "g", "g"),
        "fat_g": _off_nutrient(nutriments, "fat", "g", "g"),
        "carbs_g": _off_nutrient(nutriments, "carbohydrates", "g", "g"),
        "iron_mg": _off_nutrient(nutriments, "iron", "mg", "mg"),
        "vitamin_b12_µg": _off_nutrient(nutriments, "vitamin-b12", "µg", "µg"),
        "vitamin_d_µg": _off_nutrient(nutriments, "vitamin-d", "µg", "µg"),
        "omega_3_g": _off_nutrient(nutriments, "omega-3-fat", "g", "g"),
    }

    # OpenFoodFacts has no reliable per-piece portion data; always reports per 100g.
    entry = {"name": name or product.get("product_name") or barcode_or_query, "unit": "100g"}
    entry.update({k: _round(v) for k, v in values.items()})

    key = label or _slugify(barcode_or_query)
    _save_food(key, entry)
    return entry
