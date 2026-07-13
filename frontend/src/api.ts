import type { DailyLogResponse, Foods, ItemType, Meals } from "./types";

const API_URL = import.meta.env.VITE_API_URL;

export async function fetchFoods(): Promise<Foods> {
  const res = await fetch(`${API_URL}/foods`);
  if (!res.ok) throw new Error(`GET /foods failed: ${res.status}`);
  return res.json();
}

export async function fetchMeals(): Promise<Meals> {
  const res = await fetch(`${API_URL}/meals`);
  if (!res.ok) throw new Error(`GET /meals failed: ${res.status}`);
  return res.json();
}

export interface LogEntry {
  type: ItemType;
  key: string;
  quantity: number;
}

export async function postDailyLog(entries: LogEntry[]): Promise<DailyLogResponse> {
  const res = await fetch(`${API_URL}/daily-log`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ entries }),
  });
  if (!res.ok) throw new Error(`POST /daily-log failed: ${res.status}`);
  return res.json();
}
