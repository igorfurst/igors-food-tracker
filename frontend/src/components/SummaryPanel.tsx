import type { DailyLogResponse } from "../types";

interface SummaryPanelProps {
  dailyLog: DailyLogResponse | null;
}

function fmt(value: number | null, suffix = ""): string {
  if (value === null || value === undefined) return "—";
  return `${value}${suffix}`;
}

export default function SummaryPanel({ dailyLog }: SummaryPanelProps) {
  const intake = dailyLog?.intake;
  const garmin = dailyLog?.garmin;
  const balance = dailyLog?.balance ?? null;

  return (
    <aside className="summary-panel">
      <h2>Povzetek dneva</h2>

      <div className="summary-block">
        <h3>Dnevni vnos</h3>
        <ul>
          <li>Kalorije: {fmt(intake?.calories ?? null, " kcal")}</li>
          <li>Beljakovine: {fmt(intake?.protein_g ?? null, " g")}</li>
          <li>Maščobe: {fmt(intake?.fat_g ?? null, " g")}</li>
          <li>Ogljikovi hidrati: {fmt(intake?.carbs_g ?? null, " g")}</li>
          <li>Železo: {fmt(intake?.iron_mg ?? null, " mg")}</li>
          <li>Vitamin B12: {fmt(intake?.vitamin_b12_µg ?? null, " µg")}</li>
          <li>Vitamin D: {fmt(intake?.vitamin_d_µg ?? null, " µg")}</li>
          <li>Omega-3: {fmt(intake?.omega_3_g ?? null, " g")}</li>
        </ul>
      </div>

      <div className="summary-block">
        <h3>Garmin poraba</h3>
        <ul>
          <li>Skupaj: {fmt(garmin?.total_calories ?? null, " kcal")}</li>
          <li>Aktivnost: {fmt(garmin?.active_calories ?? null, " kcal")}</li>
          <li>BMR: {fmt(garmin?.bmr_calories ?? null, " kcal")}</li>
        </ul>
      </div>

      <div className="summary-block balance">
        <h3>Saldo (vnos − poraba)</h3>
        <p className={balance !== null && balance > 0 ? "positive" : "negative"}>
          {fmt(balance, " kcal")}
        </p>
      </div>
    </aside>
  );
}
