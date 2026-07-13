import type { Foods, ItemType, Meals, MealTime, SectionSelections } from "../types";

interface MealSectionProps {
  mealTime: MealTime;
  foods: Foods;
  meals: Meals;
  selections: SectionSelections;
  onToggle: (mealTime: MealTime, type: ItemType, key: string) => void;
  onQuantityChange: (mealTime: MealTime, type: ItemType, key: string, quantity: number) => void;
}

function itemKey(type: ItemType, key: string): string {
  return `${type}:${key}`;
}

export default function MealSection({
  mealTime,
  foods,
  meals,
  selections,
  onToggle,
  onQuantityChange,
}: MealSectionProps) {
  const foodKeys = Object.keys(foods).sort((a, b) => foods[a].name.localeCompare(foods[b].name, "sl"));
  const mealKeys = Object.keys(meals).sort((a, b) => meals[a].name.localeCompare(meals[b].name, "sl"));

  return (
    <section className="meal-section">
      <h2>{mealTime}</h2>

      <div className="item-group">
        <h3>Obroki</h3>
        <ul className="item-list">
          {mealKeys.map((key) => {
            const sel = selections[itemKey("meal", key)];
            const checked = sel?.checked ?? false;
            const quantity = sel?.quantity ?? 1;
            return (
              <li key={key} className="item-row">
                <label>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => onToggle(mealTime, "meal", key)}
                  />
                  {meals[key].name}
                </label>
                {checked && (
                  <span className="quantity-input">
                    <input
                      type="number"
                      min={0}
                      step={1}
                      value={quantity}
                      onChange={(e) =>
                        onQuantityChange(mealTime, "meal", key, Number(e.target.value))
                      }
                    />
                    <span className="unit-label">obrok(ov)</span>
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      </div>

      <div className="item-group">
        <h3>Živila</h3>
        <ul className="item-list">
          {foodKeys.map((key) => {
            const food = foods[key];
            const sel = selections[itemKey("food", key)];
            const checked = sel?.checked ?? false;
            const defaultQuantity = food.unit === "1 kos" ? 1 : 100;
            const quantity = sel?.quantity ?? defaultQuantity;
            const unitLabel = food.unit === "1 kos" ? "kos" : "g";
            return (
              <li key={key} className="item-row">
                <label>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => onToggle(mealTime, "food", key)}
                  />
                  {food.name}
                </label>
                {checked && (
                  <span className="quantity-input">
                    <input
                      type="number"
                      min={0}
                      step={food.unit === "1 kos" ? 1 : 10}
                      value={quantity}
                      onChange={(e) =>
                        onQuantityChange(mealTime, "food", key, Number(e.target.value))
                      }
                    />
                    <span className="unit-label">{unitLabel}</span>
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
