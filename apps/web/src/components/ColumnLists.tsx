import type { Profile } from "../api/client";

function ColumnList({ title, columns, empty }: { title: string; columns: string[]; empty: string }) {
  return (
    <div>
      <h3 className="mb-2 font-medium">{title}</h3>
      {columns.length > 0 ? (
        <ul className="flex flex-wrap gap-2">
          {columns.map((column) => (
            <li
              key={column}
              className="rounded-md bg-slate-100 px-2 py-1 font-mono text-xs dark:bg-slate-800"
            >
              {column}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-slate-500">{empty}</p>
      )}
    </div>
  );
}

export default function ColumnLists({ profile }: { profile: Profile }) {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      <ColumnList title="Numeric Columns" columns={profile.numeric_columns} empty="No numeric columns" />
      <ColumnList
        title="Categorical Columns"
        columns={profile.categorical_columns}
        empty="No categorical columns"
      />
    </div>
  );
}
