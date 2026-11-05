import type { AnalysisResult as Result } from "../api/client";
import DataTable from "./DataTable";

export default function AnalysisResult({ result }: { result: Result }) {
  const chart = result.chart;
  const values = chart?.data.rows.map((row) => Number(row[1] ?? row[0])).filter(Number.isFinite) ?? [];
  const max = Math.max(...values, 1);
  return (
    <div className="mt-3 space-y-3 border-t border-slate-200 pt-3 text-sm dark:border-slate-700">
      <span className="rounded-full bg-indigo-100 px-2 py-1 text-xs font-medium text-indigo-700 dark:bg-indigo-950 dark:text-indigo-200">{result.method}</span>
      {result.statistics && <pre className="overflow-auto rounded bg-slate-950 p-3 text-xs text-slate-100">{JSON.stringify(result.statistics, null, 2)}</pre>}
      {result.anomalies && <p>Potential anomalies: <strong>{result.anomalies.count}</strong> ({result.anomalies.method})</p>}
      {chart && chart.type !== "table" && <div className="space-y-2"><p className="font-medium">{chart.title}</p><div className="space-y-1">{chart.data.rows.slice(0, 12).map((row, index) => <div key={index} className="grid grid-cols-[8rem_1fr] items-center gap-2"><span className="truncate">{String(row[0])}</span><div className="h-5 rounded bg-indigo-500" style={{ width: `${Math.max(3, (Number(row[1] ?? row[0]) / max) * 100)}%` }} /></div>)}</div></div>}
      {result.tables.map((item, index) => <DataTable key={index} table={item} />)}
    </div>
  );
}
