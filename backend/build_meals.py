import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

from nutrition_service import DATA_DIR, NUTRIENT_KEYS

FOODS_FILE = DATA_DIR / "foods.json"
MEALS_FILE = DATA_DIR / "meals.json"

MEALS = [
    {
        "key": "losos_zelenjava",
        "name": "Losos z zelenjavo",
        "ingredients": [
            {"food": "salmon", "quantity": 200},
            {"food": "broccoli_raw", "quantity": 150},
            {"food": "carrots_raw", "quantity": 100},
        ],
    },
    {
        "key": "losos_krompir",
        "name": "Losos s krompirjem",
        "ingredients": [
            {"food": "salmon", "quantity": 200},
            {"food": "potato", "quantity": 250},
        ],
    },
    {
        "key": "piscanec_zelena_solata",
        "name": "Piščanec v zeleni solati",
        "ingredients": [
            {"food": "chicken_broilers_or_fryers_breast_meat_only_raw", "quantity": 400},
            {"food": "lettuce_raw", "quantity": 100},
            {"food": "olive_oil", "quantity": 13.5},
        ],
    },
    {
        "key": "rizota_meso",
        "name": "Rižota z mesom",
        "ingredients": [
            {"food": "white_rice", "quantity": 80},
            {"food": "beef", "quantity": 150},
            {"food": "onions_raw", "quantity": 50},
        ],
    },
    {
        "key": "rizota_tuna",
        "name": "Rižota s tuno",
        "ingredients": [
            {"food": "white_rice", "quantity": 80},
            {"food": "tuna", "quantity": 150},
            {"food": "onions_raw", "quantity": 50},
        ],
    },
    {
        "key": "tortilja_piscanec",
        "name": "Tortilja s piščancem",
        "ingredients": [
            {"food": "tortilla_flour", "quantity": 1},
            {"food": "chicken_broilers_or_fryers_breast_meat_only_raw", "quantity": 300},
            {"food": "lettuce_raw", "quantity": 50},
        ],
    },
    {
        "key": "zelenjavni_polpet",
        "name": "Zelenjavni polpet",
        "ingredients": [
            {"food": "zucchini_raw", "quantity": 150},
            {"food": "carrots_raw", "quantity": 100},
            {"food": "egg_whole_raw", "quantity": 1},
        ],
    },
    {
        "key": "zelenjavna_juha",
        "name": "Zelenjavna juha",
        "ingredients": [
            {"food": "vegetable_soup", "quantity": 300},
        ],
    },
    {
        "key": "goveji_zrezek_krompir_zelenjava",
        "name": "Goveji zrezek s krompirjem in zelenjavo",
        "ingredients": [
            {"food": "beef", "quantity": 200},
            {"food": "potato", "quantity": 200},
            {"food": "broccoli_raw", "quantity": 100},
        ],
    },
    {
        "key": "testenine_tuna_paradiznik",
        "name": "Testenine s tuno in paradižnikovo omako",
        "ingredients": [
            {"food": "pasta", "quantity": 100},
            {"food": "tuna", "quantity": 150},
            {"food": "tomatoes_raw", "quantity": 150},
        ],
    },
    {
        "key": "omleta_jajca_zelenjava",
        "name": "Omleta z jajci in zelenjavo",
        "ingredients": [
            {"food": "egg_whole_raw", "quantity": 4},
            {"food": "peppers_sweet_raw", "quantity": 100},
            {"food": "onions_raw", "quantity": 50},
        ],
    },
]

NOTES = [
    "olive_oil: kolicina 13.5 g je standardna pretvorba za 1 jedilno zlico olivnega olja.",
]


def _unit_label(food_unit):
    return "kos" if food_unit == "1 kos" else "g"


def compute_meal_totals(ingredients, foods):
    totals = {k: None for k in NUTRIENT_KEYS}
    for ing in ingredients:
        food = foods[ing["food"]]
        scale = ing["quantity"] if food["unit"] == "1 kos" else ing["quantity"] / 100
        for key in NUTRIENT_KEYS:
            value = food[key]
            if value is not None:
                totals[key] = round((totals[key] or 0) + value * scale, 3)
    return totals


def main():
    foods = json.loads(FOODS_FILE.read_text(encoding="utf-8"))
    meals = {}

    for meal in MEALS:
        ingredients_out = [
            {
                "food": ing["food"],
                "quantity": ing["quantity"],
                "unit": _unit_label(foods[ing["food"]]["unit"]),
            }
            for ing in meal["ingredients"]
        ]
        totals = compute_meal_totals(meal["ingredients"], foods)
        meals[meal["key"]] = {
            "name": meal["name"],
            "ingredients": ingredients_out,
            **totals,
        }

    MEALS_FILE.write_text(json.dumps(meals, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Zapisanih {len(meals)} obrokov v {MEALS_FILE}")
    if NOTES:
        print()
        print("Opombe:")
        for note in NOTES:
            print(f" - {note}")


if __name__ == "__main__":
    main()
