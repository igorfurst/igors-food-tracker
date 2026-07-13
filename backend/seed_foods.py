import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

from nutrition_service import fetch_from_openfoodfacts, fetch_from_usda

FOODS = [
    {"name": "Govedina", "query": "beef", "unit": "100g"},
    {"name": "Teletina", "query": "veal", "unit": "100g"},
    {"name": "Svinjina", "query": "pork", "unit": "100g"},
    {"name": "Piščanec", "query": "chicken, broilers or fryers, breast, meat only, raw", "unit": "100g"},
    {"name": "Puran", "query": "turkey breast", "unit": "100g"},
    {"name": "Raca", "query": "duck", "unit": "100g"},
    {"name": "Jagnjetina", "query": "lamb", "unit": "100g"},
    {"name": "Divjačina", "query": "venison", "unit": "100g"},
    {"name": "Salama", "query": "salami", "unit": "100g"},
    {"name": "Pršut", "query": "prosciutto", "unit": "100g"},
    {"name": "Šunka", "query": "ham", "unit": "100g"},
    {"name": "Hrenovke", "query": "hot dog sausage", "unit": "100g"},
    {"name": "Klobasa", "query": "sausage", "unit": "100g"},
    {"name": "Pašteta", "query": "liver pate", "unit": "100g"},
    {"name": "Slanina", "query": "bacon", "unit": "100g"},
    {"name": "Losos", "query": "salmon", "unit": "100g"},
    {"name": "Tuna", "query": "tuna, fresh, raw", "unit": "100g"},
    {"name": "Sardine", "query": "sardines", "unit": "100g"},
    {"name": "Skuša", "query": "mackerel", "unit": "100g"},
    {"name": "Oslič", "query": "hake", "unit": "100g"},
    {"name": "Trska", "query": "cod", "unit": "100g"},
    {"name": "Brancin", "query": "sea bass", "unit": "100g"},
    {"name": "Orada", "query": "sea bream", "unit": "100g"},
    {"name": "Kozice", "query": "shrimp", "unit": "100g"},
    {"name": "Lignji", "query": "squid", "unit": "100g"},
    {"name": "Hobotnica", "query": "octopus", "unit": "100g"},
    {"name": "Školjke", "query": "mussels", "unit": "100g"},
    {"name": "Sushi", "query": "sushi", "unit": "100g"},
    {"name": "Sir", "query": "cheddar cheese", "unit": "100g"},
    {"name": "Skuta", "query": "cottage cheese", "unit": "100g"},
    {"name": "Jogurt", "query": "plain yogurt", "unit": "100g"},
    {"name": "Grški jogurt", "query": "yogurt, greek, plain, whole milk", "unit": "100g"},
    {"name": "Kefir", "query": "kefir", "unit": "100g"},
    {"name": "Kisla smetana", "query": "sour cream", "unit": "100g"},
    {"name": "Maslo", "query": "butter", "unit": "100g"},
    {"name": "Mleko", "query": "milk, whole, 3.25% milkfat", "unit": "100g"},
    {"name": "Mozzarella", "query": "mozzarella cheese", "unit": "100g"},
    {"name": "Parmezan", "query": "parmesan cheese", "unit": "100g"},
    {"name": "Feta", "query": "feta cheese", "unit": "100g"},
    {"name": "Skyr", "query": "skyr", "unit": "100g"},
    {"name": "Jajca", "query": "egg, whole, raw", "unit": "1 kos"},
    {"name": "Bel kruh", "query": "white bread", "unit": "100g"},
    {"name": "Polnozrnat kruh", "query": "whole wheat bread", "unit": "100g"},
    {"name": "Ržen kruh", "query": "rye bread", "unit": "100g"},
    {"name": "Toast", "query": "white bread, toasted", "unit": "1 kos"},
    {"name": "Žemlja", "query": "dinner roll", "unit": "1 kos"},
    {"name": "Tortilja", "query": "tortilla, flour", "unit": "1 kos"},
    {"name": "Riž", "query": "white rice", "unit": "100g"},
    {"name": "Rjavi riž", "query": "brown rice", "unit": "100g"},
    {"name": "Basmati riž", "query": "basmati rice", "unit": "100g"},
    {"name": "Jasminov riž", "query": "jasmine rice", "unit": "100g"},
    {"name": "Krompir", "query": "potatoes, flesh and skin, raw", "unit": "100g"},
    {"name": "Sladki krompir", "query": "sweet potato", "unit": "100g"},
    {"name": "Testenine", "query": "pasta", "unit": "100g"},
    {"name": "Polenta", "query": "polenta", "unit": "100g"},
    {"name": "Kuskus", "query": "couscous", "unit": "100g"},
    {"name": "Bulgur", "query": "bulgur", "unit": "100g"},
    {"name": "Kamut", "query": "kamut wheat", "unit": "100g"},
    {"name": "Ajda", "query": "buckwheat", "unit": "100g"},
    {"name": "Ječmen", "query": "barley", "unit": "100g"},
    {"name": "Proso", "query": "millet", "unit": "100g"},
    {"name": "Ovseni kosmiči", "query": "oats", "unit": "100g"},
    {"name": "Kvinoja", "query": "quinoa", "unit": "100g"},
    {"name": "Fižol", "query": "kidney beans", "unit": "100g"},
    {"name": "Grah", "query": "green peas", "unit": "100g"},
    {"name": "Leča", "query": "lentils", "unit": "100g"},
    {"name": "Čičerika", "query": "chickpeas", "unit": "100g"},
    {"name": "Soja", "query": "soybeans, mature seeds, raw", "unit": "100g"},
    {"name": "Bob", "query": "fava beans", "unit": "100g"},
    {"name": "Goveja juha", "query": "beef broth", "unit": "100g"},
    {"name": "Piščančja juha", "query": "chicken soup", "unit": "100g"},
    {"name": "Gobova juha", "query": "mushroom soup", "unit": "100g"},
    {"name": "Paradižnikova juha", "query": "tomato soup", "unit": "100g"},
    {"name": "Zelenjavna juha", "query": "vegetable soup", "unit": "100g"},
    {"name": "Orehi", "query": "walnuts", "unit": "100g"},
    {"name": "Lešniki", "query": "hazelnuts", "unit": "100g"},
    {"name": "Mandlji", "query": "almonds", "unit": "100g"},
    {"name": "Indijski oreščki", "query": "cashews", "unit": "100g"},
    {"name": "Pistacije", "query": "pistachios", "unit": "100g"},
    {"name": "Pekan orehi", "query": "pecans", "unit": "100g"},
    {"name": "Brazilski oreščki", "query": "brazil nuts", "unit": "100g"},
    {"name": "Makadamija", "query": "macadamia nuts", "unit": "100g"},
    {"name": "Pinjole", "query": "pine nuts", "unit": "100g"},
    {"name": "Arašidi", "query": "peanuts", "unit": "100g"},
    {"name": "Sončnična semena", "query": "sunflower seeds", "unit": "100g"},
    {"name": "Bučna semena", "query": "pumpkin seeds", "unit": "100g"},
    {"name": "Chia semena", "query": "chia seeds", "unit": "100g"},
    {"name": "Lanena semena", "query": "flaxseed", "unit": "100g"},
    {"name": "Sezam", "query": "sesame seeds", "unit": "100g"},
    {"name": "Jabolko", "query": "apple, raw", "unit": "1 kos"},
    {"name": "Hruška", "query": "pear, raw", "unit": "1 kos"},
    {"name": "Ringlo", "query": "greengage plum, raw", "unit": "1 kos"},
    {"name": "Sliva", "query": "plum, raw", "unit": "1 kos"},
    {"name": "Češnja", "query": "sweet cherries, raw", "unit": "100g"},
    {"name": "Višnja", "query": "sour cherries, raw", "unit": "100g"},
    {"name": "Breskev", "query": "peach, raw", "unit": "1 kos"},
    {"name": "Nektarina", "query": "nectarine, raw", "unit": "1 kos"},
    {"name": "Marelica", "query": "apricots, raw", "unit": "100g"},
    {"name": "Grozdje", "query": "grapes, raw", "unit": "100g"},
    {"name": "Jagode", "query": "strawberries, raw", "unit": "100g"},
    {"name": "Maline", "query": "raspberries, raw", "unit": "100g"},
    {"name": "Borovnice", "query": "blueberries, raw", "unit": "100g"},
    {"name": "Robide", "query": "blackberries, raw", "unit": "100g"},
    {"name": "Ribez", "query": "red currants, raw", "unit": "100g"},
    {"name": "Kivi", "query": "kiwifruit, raw", "unit": "1 kos"},
    {"name": "Banana", "query": "banana, raw", "unit": "1 kos"},
    {"name": "Pomaranča", "query": "orange, raw", "unit": "1 kos"},
    {"name": "Mandarina", "query": "tangerine, raw", "unit": "1 kos"},
    {"name": "Limona", "query": "lemon, raw", "unit": "1 kos"},
    {"name": "Grenivka", "query": "grapefruit, raw", "unit": "1 kos"},
    {"name": "Ananas", "query": "pineapple, raw", "unit": "100g"},
    {"name": "Mango", "query": "mango, raw", "unit": "1 kos"},
    {"name": "Avokado", "query": "avocado, raw", "unit": "1 kos"},
    {"name": "Melona", "query": "cantaloupe, raw", "unit": "100g"},
    {"name": "Lubenica", "query": "watermelon, raw", "unit": "100g"},
    {"name": "Kaki", "query": "persimmon, raw", "unit": "1 kos"},
    {"name": "Fige", "query": "figs, raw", "unit": "100g"},
    {"name": "Datlji", "query": "dates", "unit": "100g"},
    {"name": "Zelena solata", "query": "lettuce, raw", "unit": "100g"},
    {"name": "Radič", "query": "radicchio, raw", "unit": "100g"},
    {"name": "Motovilec", "query": "lamb's lettuce, raw", "unit": "100g"},
    {"name": "Rukola", "query": "arugula, raw", "unit": "100g"},
    {"name": "Zelje", "query": "cabbage, raw", "unit": "100g"},
    {"name": "Kislo zelje", "query": "sauerkraut", "unit": "100g"},
    {"name": "Paradižnik", "query": "tomatoes, raw", "unit": "100g"},
    {"name": "Paprika", "query": "peppers, sweet, raw", "unit": "100g"},
    {"name": "Kumara", "query": "cucumber, raw", "unit": "100g"},
    {"name": "Korenje", "query": "carrots, raw", "unit": "100g"},
    {"name": "Čebula", "query": "onions, raw", "unit": "100g"},
    {"name": "Česen", "query": "garlic, raw", "unit": "100g"},
    {"name": "Brokoli", "query": "broccoli, raw", "unit": "100g"},
    {"name": "Cvetača", "query": "cauliflower, raw", "unit": "100g"},
    {"name": "Bučke", "query": "zucchini, raw", "unit": "100g"},
    {"name": "Jajčevec", "query": "eggplant, raw", "unit": "100g"},
    {"name": "Špinača", "query": "spinach, raw", "unit": "100g"},
    {"name": "Blitva", "query": "swiss chard, raw", "unit": "100g"},
    {"name": "Ohrovt", "query": "kale, raw", "unit": "100g"},
    {"name": "Brstični ohrovt", "query": "brussels sprouts, raw", "unit": "100g"},
    {"name": "Zelena", "query": "celery, raw", "unit": "100g"},
    {"name": "Redkev", "query": "radishes, raw", "unit": "100g"},
    {"name": "Rdeča pesa", "query": "beets, raw", "unit": "100g"},
    {"name": "Koruza", "query": "corn, sweet, raw", "unit": "100g"},
    {"name": "Gobe", "query": "mushrooms, raw", "unit": "100g"},
    {"name": "Beluši", "query": "asparagus, raw", "unit": "100g"},
    {"name": "Olive", "query": "olives", "unit": "100g"},
    {"name": "Kisle kumarice", "query": "pickles", "unit": "100g"},
    {"name": "Kisla repa", "query": "fermented turnip", "unit": "100g"},
    {"name": "Oljčno olje", "query": "olive oil", "unit": "100g"},
    {"name": "Bučno olje", "query": "pumpkin seed oil", "unit": "100g"},
    {"name": "Sončnično olje", "query": "sunflower oil", "unit": "100g"},
    {"name": "Repično olje", "query": "canola oil", "unit": "100g"},
    {"name": "Kokosovo olje", "query": "coconut oil", "unit": "100g"},
    {"name": "Med", "query": "honey", "unit": "100g"},
    {"name": "Marmelada", "query": "jam", "unit": "100g"},
    {"name": "Arašidovo maslo", "query": "peanut butter", "unit": "100g"},
    {"name": "Lešnikov namaz", "query": "hazelnut spread", "unit": "100g"},
    {"name": "Voda", "query": "water", "unit": "100g"},
    {"name": "Mineralna voda", "query": "mineral water", "unit": "100g"},
    {"name": "Kava", "query": "coffee, black", "unit": "100g"},
    {"name": "Čaj", "query": "tea, brewed", "unit": "100g"},
    {"name": "Kakav", "query": "cocoa powder", "unit": "100g"},
    {"name": "Sadni sok", "query": "fruit juice", "unit": "100g"},
    {"name": "Pomarančni sok", "query": "orange juice", "unit": "100g"},
    {"name": "Rdeče vino", "query": "red wine", "unit": "100g"},
    {"name": "Belo vino", "query": "white wine", "unit": "100g"},
]


def _fetch_with_retries(fn, food, attempts=3, delay=1.5):
    last_error = None
    for attempt in range(attempts):
        try:
            return fn(food["query"], name=food["name"], unit=food["unit"])
        except Exception as e:
            last_error = e
            if attempt < attempts - 1:
                time.sleep(delay)
    raise last_error


def main():
    not_found = []

    for food in FOODS:
        try:
            entry = _fetch_with_retries(fetch_from_usda, food)
            print(f"[USDA] {food['name']} -> {entry['name']} ({entry['unit']})")
        except Exception:
            try:
                entry = _fetch_with_retries(fetch_from_openfoodfacts, food)
                print(f"[OFF]  {food['name']} -> {entry['name']} ({entry['unit']})")
            except Exception as e:
                print(f"[MANJKA] {food['name']} ({e})")
                not_found.append(food["name"])
        time.sleep(0.8)

    print()
    print(f"Ni bilo mogoce najti {len(not_found)} od {len(FOODS)} zivil:")
    for name in not_found:
        print(f" - {name}")


if __name__ == "__main__":
    main()
