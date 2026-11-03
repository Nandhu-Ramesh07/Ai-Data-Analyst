import type { Cell, Table } from "../api/client";

function formatCell(value: Cell) {
  if (value === null) return <span className="text-slate-400">—</span>;

  if (typeof value === "number" && !Number.isInteger(value)) {
    return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
  }

  return String(value);
}

export default function DataTable({ table }: { table: Table }) {
  return (
    <div className="overflow-x-auto rounded-lg ring-1 ring-slate-200 dark:ring-slate-800">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 dark:bg-slate-950">
          <tr>
            {table.columns.map((column, index) => (
              <th
                key={index}
                className="whitespace-nowrap px-3 py-2 text-left font-semibold text-slate-600 dark:text-slate-300"
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
          {table.rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
              {row.map((value, cellIndex) => (
                <td
                  key={cellIndex}
                  className={`whitespace-nowrap px-3 py-2 ${
                    typeof value === "number" ? "text-right tabular-nums" : ""
                  }`}
                >
                  {formatCell(value)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
