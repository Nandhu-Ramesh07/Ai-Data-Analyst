import type { Profile } from "../api/client";

export default function SummaryCards({ profile }: { profile: Profile }) {
  const cards = [
    { label: "Rows", value: profile.rows },
    { label: "Columns", value: profile.columns },
    { label: "Duplicates", value: profile.duplicates },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-lg bg-slate-50 p-4 ring-1 ring-slate-200 dark:bg-slate-950 dark:ring-slate-800"
        >
          <div className="text-sm text-slate-500">{card.label}</div>
          <div className="mt-1 text-3xl font-semibold tabular-nums">
            {card.value.toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
}
