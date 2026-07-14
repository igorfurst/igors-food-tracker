import type { Selection } from "../types";

export interface ListEntry {
  key: string;
  name: string;
  unitLabel: string;
  defaultQuantity: number;
  quantityStep: number;
}

interface ItemListSectionProps {
  title: string;
  items: ListEntry[];
  selections: Record<string, Selection>;
  onToggle: (key: string, defaultQuantity: number) => void;
  onQuantityChange: (key: string, quantity: number) => void;
}

export default function ItemListSection({
  title,
  items,
  selections,
  onToggle,
  onQuantityChange,
}: ItemListSectionProps) {
  return (
    <section className="meal-section">
      <h2>{title}</h2>
      <ul className="item-list">
        {items.map((item) => {
          const sel = selections[item.key];
          const checked = sel?.checked ?? false;
          const quantity = sel?.quantity ?? item.defaultQuantity;
          return (
            <li key={item.key} className="item-row">
              <label>
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => onToggle(item.key, item.defaultQuantity)}
                />
                {item.name}
              </label>
              {checked && (
                <span className="quantity-input">
                  <input
                    type="number"
                    min={0}
                    step={item.quantityStep}
                    value={quantity}
                    onChange={(e) => onQuantityChange(item.key, Number(e.target.value))}
                  />
                  <span className="unit-label">{item.unitLabel}</span>
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
