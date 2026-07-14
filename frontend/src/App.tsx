import { useEffect, useMemo, useState } from "react";
import { fetchFoods, fetchMeals, postDailyLog, type LogEntry } from "./api";
import AddFoodForm from "./components/AddFoodForm";
import ItemListSection, { type ListEntry } from "./components/ItemListSection";
import SummaryPanel from "./components/SummaryPanel";
import type { AllSelections, DailyLogResponse, FoodItem, Foods, ItemType, Meals } from "./types";
import "./App.css";

function compositeKey(type: ItemType, key: string): string {
  return `${type}:${key}`;
}

function sortedByName<T extends { name: string }>(entries: [string, T][]): [string, T][] {
  return [...entries].sort((a, b) => a[1].name.localeCompare(b[1].name, "sl"));
}

function App() {
  const [foods, setFoods] = useState<Foods>({});
  const [meals, setMeals] = useState<Meals>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selections, setSelections] = useState<AllSelections>({});
  const [dailyLog, setDailyLog] = useState<DailyLogResponse | null>(null);

  useEffect(() => {
    Promise.all([fetchFoods(), fetchMeals()])
      .then(([foodsData, mealsData]) => {
        setFoods(foodsData);
        setMeals(mealsData);
      })
      .catch((err) => setError(String(err)))
      .finally(() => setLoading(false));
  }, []);

  const entries = useMemo<LogEntry[]>(() => {
    const result: LogEntry[] = [];
    for (const [key, sel] of Object.entries(selections)) {
      if (sel.checked) {
        const [type, itemId] = key.split(":") as [ItemType, string];
        result.push({ type, key: itemId, quantity: sel.quantity });
      }
    }
    return result;
  }, [selections]);

  useEffect(() => {
    if (entries.length === 0) {
      setDailyLog(null);
      return;
    }
    const timeout = setTimeout(() => {
      postDailyLog(entries)
        .then(setDailyLog)
        .catch((err) => setError(String(err)));
    }, 400);
    return () => clearTimeout(timeout);
  }, [entries]);

  function handleToggle(type: ItemType, key: string, defaultQuantity: number) {
    setSelections((prev) => {
      const compositeId = compositeKey(type, key);
      const existing = prev[compositeId];
      if (existing?.checked) {
        return { ...prev, [compositeId]: { ...existing, checked: false } };
      }
      return { ...prev, [compositeId]: { checked: true, quantity: existing?.quantity ?? defaultQuantity } };
    });
  }

  function handleQuantityChange(type: ItemType, key: string, quantity: number) {
    setSelections((prev) => ({
      ...prev,
      [compositeKey(type, key)]: { checked: true, quantity },
    }));
  }

  function handleFoodAdded(key: string, food: FoodItem) {
    setFoods((prev) => ({ ...prev, [key]: food }));
  }

  if (loading) return <p className="status">Nalaganje...</p>;
  if (error) return <p className="status error">Napaka: {error}</p>;

  const breakfastMeals: ListEntry[] = sortedByName(Object.entries(meals)).flatMap(([key, meal]) =>
    meal.category === "zajtrk"
      ? [{ key, name: meal.name, unitLabel: "obrok(ov)", defaultQuantity: 1, quantityStep: 1 }]
      : [],
  );

  const lunchDinnerMeals: ListEntry[] = sortedByName(Object.entries(meals)).flatMap(([key, meal]) =>
    meal.category === "kosilo_vecerja"
      ? [{ key, name: meal.name, unitLabel: "obrok(ov)", defaultQuantity: 1, quantityStep: 1 }]
      : [],
  );

  const foodItems: ListEntry[] = sortedByName(Object.entries(foods)).map(([key, food]) => ({
    key,
    name: food.name,
    unitLabel: food.unit === "1 kos" ? "kos" : "g",
    defaultQuantity: food.unit === "1 kos" ? 1 : 100,
    quantityStep: food.unit === "1 kos" ? 1 : 10,
  }));

  return (
    <div className="app-layout">
      <main className="sections">
        <h1>Igor's Food Tracker</h1>

        <ItemListSection
          title="Zajtrk"
          items={breakfastMeals}
          selections={selections}
          onToggle={(key, defaultQuantity) => handleToggle("meal", key, defaultQuantity)}
          onQuantityChange={(key, quantity) => handleQuantityChange("meal", key, quantity)}
        />

        <ItemListSection
          title="Kosilo / Večerja"
          items={lunchDinnerMeals}
          selections={selections}
          onToggle={(key, defaultQuantity) => handleToggle("meal", key, defaultQuantity)}
          onQuantityChange={(key, quantity) => handleQuantityChange("meal", key, quantity)}
        />

        <ItemListSection
          title="Živila"
          items={foodItems}
          selections={selections}
          onToggle={(key, defaultQuantity) => handleToggle("food", key, defaultQuantity)}
          onQuantityChange={(key, quantity) => handleQuantityChange("food", key, quantity)}
        />

        <AddFoodForm onAdded={handleFoodAdded} />
      </main>
      <SummaryPanel dailyLog={dailyLog} />
    </div>
  );
}

export default App;
