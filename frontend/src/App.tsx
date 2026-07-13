import { useEffect, useMemo, useState } from "react";
import { fetchFoods, fetchMeals, postDailyLog, type LogEntry } from "./api";
import MealSection from "./components/MealSection";
import SummaryPanel from "./components/SummaryPanel";
import {
  MEAL_TIMES,
  type AllSelections,
  type DailyLogResponse,
  type Foods,
  type ItemType,
  type Meals,
  type MealTime,
} from "./types";
import "./App.css";

function itemKey(type: ItemType, key: string): string {
  return `${type}:${key}`;
}

function emptySelections(): AllSelections {
  return {
    Zajtrk: {},
    Kosilo: {},
    Večerja: {},
  };
}

function App() {
  const [foods, setFoods] = useState<Foods>({});
  const [meals, setMeals] = useState<Meals>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selections, setSelections] = useState<AllSelections>(emptySelections());
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
    for (const mealTime of MEAL_TIMES) {
      for (const [key, sel] of Object.entries(selections[mealTime])) {
        if (sel.checked) {
          const [type, itemId] = key.split(":") as [ItemType, string];
          result.push({ type, key: itemId, quantity: sel.quantity });
        }
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

  function handleToggle(mealTime: MealTime, type: ItemType, key: string) {
    setSelections((prev) => {
      const section = { ...prev[mealTime] };
      const compositeKey = itemKey(type, key);
      const existing = section[compositeKey];
      if (existing?.checked) {
        section[compositeKey] = { ...existing, checked: false };
      } else {
        const defaultQuantity =
          type === "meal" ? 1 : foods[key]?.unit === "1 kos" ? 1 : 100;
        section[compositeKey] = { checked: true, quantity: existing?.quantity ?? defaultQuantity };
      }
      return { ...prev, [mealTime]: section };
    });
  }

  function handleQuantityChange(mealTime: MealTime, type: ItemType, key: string, quantity: number) {
    setSelections((prev) => {
      const section = { ...prev[mealTime] };
      const compositeKey = itemKey(type, key);
      section[compositeKey] = { checked: true, quantity };
      return { ...prev, [mealTime]: section };
    });
  }

  if (loading) return <p className="status">Nalaganje...</p>;
  if (error) return <p className="status error">Napaka: {error}</p>;

  return (
    <div className="app-layout">
      <main className="sections">
        <h1>Igor's Food Tracker</h1>
        {MEAL_TIMES.map((mealTime) => (
          <MealSection
            key={mealTime}
            mealTime={mealTime}
            foods={foods}
            meals={meals}
            selections={selections[mealTime]}
            onToggle={handleToggle}
            onQuantityChange={handleQuantityChange}
          />
        ))}
      </main>
      <SummaryPanel dailyLog={dailyLog} />
    </div>
  );
}

export default App;
