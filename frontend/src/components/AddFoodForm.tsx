import { useState } from "react";
import { lookupFood } from "../api";
import type { FoodItem } from "../types";

interface AddFoodFormProps {
  onAdded: (key: string, food: FoodItem) => void;
}

export default function AddFoodForm({ onAdded }: AddFoodFormProps) {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;

    setLoading(true);
    setError(null);
    try {
      const { key, ...food } = await lookupFood(trimmed);
      onAdded(key, food);
      setName("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="add-food-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Dodaj novo živilo/obrok (ime)"
        value={name}
        onChange={(e) => setName(e.target.value)}
        disabled={loading}
      />
      <button type="submit" disabled={loading || !name.trim()}>
        {loading ? "Iščem…" : "Dodaj"}
      </button>
      {error && <p className="add-food-error">{error}</p>}
    </form>
  );
}
