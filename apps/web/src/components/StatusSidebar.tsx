import type { Health } from "../api/client";

interface StatusSidebarProps {
  health: Health | null;
  apiOnline: boolean;
  filename: string | null;
}

type Tone = "ok" | "info" | "warn" | "error";

const toneClasses: Record<Tone, string> = {
  ok: "bg-emerald-50 text-emerald-800 ring-emerald-200 dark:bg-emerald-950 dark:text-emerald-200 dark:ring-emerald-900",
  info: "bg-sky-50 text-sky-800 ring-sky-200 dark:bg-sky-950 dark:text-sky-200 dark:ring-sky-900",
  warn: "bg-amber-50 text-amber-800 ring-amber-200 dark:bg-amber-950 dark:text-amber-200 dark:ring-amber-900",
  error: "bg-rose-50 text-rose-800 ring-rose-200 dark:bg-rose-950 dark:text-rose-200 dark:ring-rose-900",
};

function Badge({ tone, children }: { tone: Tone; children: string }) {
  return (
    <div className={`rounded-lg px-3 py-2 text-sm ring-1 ${toneClasses[tone]}`}>
      {children}
    </div>
  );
}

function modelStatus(health: Health | null, apiOnline: boolean): [Tone, string] {
  if (!apiOnline) return ["error", "🔴 API not reachable"];
  if (!health || health.model_ready === null) return ["warn", "🟡 Loading model…"];
  if (health.model_ready) return ["ok", `🟢 ${health.model} ready`];
  return ["error", "🔴 Ollama not available"];
}

export default function StatusSidebar({ health, apiOnline, filename }: StatusSidebarProps) {
  const [tone, label] = modelStatus(health, apiOnline);

  return (
    <aside className="flex flex-col gap-6 border-slate-200 bg-white p-5 lg:min-h-screen lg:w-72 lg:shrink-0 lg:border-r dark:border-slate-800 dark:bg-slate-900">
      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Project Status
        </h3>
        {filename ? (
          <Badge tone="ok">✅ Dataset loaded</Badge>
        ) : (
          <Badge tone="info">📂 No dataset uploaded</Badge>
        )}
      </div>

      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          AI Status
        </h3>
        <Badge tone={tone}>{label}</Badge>
      </div>

      {filename && (
        <div>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Dataset
          </h3>
          <p className="break-all text-sm">
            <span className="font-medium">File:</span> {filename}
          </p>
        </div>
      )}
    </aside>
  );
}
