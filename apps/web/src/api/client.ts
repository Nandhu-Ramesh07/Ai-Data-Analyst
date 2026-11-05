export type Cell = string | number | boolean | null;

export interface Table {
  columns: string[];
  rows: Cell[][];
}

export interface Profile {
  rows: number;
  columns: number;
  duplicates: number;
  column_names: string[];
  numeric_columns: string[];
  categorical_columns: string[];
  missing_values: Record<string, number>;
  missing_percentages: Record<string, number>;
  dtypes: Record<string, string>;
  column_profiles?: Record<string, { distinct: number; missing: number; sample_values: string[] }>;
  quality_warnings?: string[];
}

export interface Chart {
  type: "bar" | "histogram" | "table";
  title: string;
  x?: string;
  y?: string;
  data: Table;
}

export interface AnalysisResult {
  conversation_id: string;
  method: string;
  message: string;
  tables: Table[];
  chart?: Chart;
  profile?: Profile;
  statistics?: Record<string, unknown>;
  anomalies?: { count: number; method: string; threshold?: string };
}

export interface Conversation { id: string; dataset_id: string; title: string; created_at?: string }
export interface StoredMessage { id: string; role: "user" | "assistant"; content: string; result?: AnalysisResult; created_at?: string }

export interface Dataset {
  id: string;
  filename: string;
  profile: Profile;
  preview: Table;
  numeric_stats: Table | null;
}

export interface Health {
  model: string;
  // null while the model is still warming up
  model_ready: boolean | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init);

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;

    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // keep the status text
    }

    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export function getHealth(): Promise<Health> {
  return request<Health>("/health");
}

export function uploadDataset(file: File): Promise<Dataset> {
  const form = new FormData();
  form.append("file", file);

  return request<Dataset>("/datasets", { method: "POST", body: form });
}

export function getDataset(id: string): Promise<Dataset> {
  return request<Dataset>(`/datasets/${id}`);
}

export async function askQuestion(id: string, question: string, conversationId?: string): Promise<AnalysisResult> {
  return request<AnalysisResult>(`/datasets/${id}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, conversation_id: conversationId }),
  });
}

export async function downloadReport(id: string, conversationId?: string): Promise<void> {
  const response = await fetch(`/api/datasets/${id}/reports${conversationId ? `?conversation_id=${encodeURIComponent(conversationId)}` : ""}`, { method: "POST" });
  if (!response.ok) throw new Error("Could not generate report");
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url; link.download = "analysis-report.pdf"; link.click(); URL.revokeObjectURL(url);
}

export function getConversations(datasetId: string): Promise<Conversation[]> {
  return request(`/datasets/${datasetId}/conversations`);
}

export function getConversationMessages(datasetId: string, conversationId: string): Promise<StoredMessage[]> {
  return request(`/datasets/${datasetId}/conversations/${conversationId}`);
}
