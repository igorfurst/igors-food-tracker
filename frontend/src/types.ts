export interface FoodItem {
  name: string;
  unit: string;
  calories: number | null;
  protein_g: number | null;
  fat_g: number | null;
  carbs_g: number | null;
  iron_mg: number | null;
  vitamin_b12_µg: number | null;
  vitamin_d_µg: number | null;
  omega_3_g: number | null;
}

export type Foods = Record<string, FoodItem>;

export interface MealIngredient {
  food: string;
  quantity: number;
  unit: string;
}

export interface MealItem {
  name: string;
  ingredients: MealIngredient[];
  calories: number | null;
  protein_g: number | null;
  fat_g: number | null;
  carbs_g: number | null;
  iron_mg: number | null;
  vitamin_b12_µg: number | null;
  vitamin_d_µg: number | null;
  omega_3_g: number | null;
}

export type Meals = Record<string, MealItem>;

export const MEAL_TIMES = ["Zajtrk", "Kosilo", "Večerja"] as const;
export type MealTime = (typeof MEAL_TIMES)[number];

export type ItemType = "food" | "meal";

export interface Selection {
  checked: boolean;
  quantity: number;
}

export type SectionSelections = Record<string, Selection>;
export type AllSelections = Record<MealTime, SectionSelections>;

export interface NutrientTotals {
  calories: number | null;
  protein_g: number | null;
  fat_g: number | null;
  carbs_g: number | null;
  iron_mg: number | null;
  vitamin_b12_µg: number | null;
  vitamin_d_µg: number | null;
  omega_3_g: number | null;
}

export interface GarminData {
  total_calories: number | null;
  active_calories: number | null;
  bmr_calories: number | null;
}

export interface DailyLogResponse {
  intake: NutrientTotals;
  garmin: GarminData | null;
  balance: number | null;
}
