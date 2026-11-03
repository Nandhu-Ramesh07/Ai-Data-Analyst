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
}

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

export async function askQuestion(id: string, question: string): Promise<string> {
  const { answer } = await request<{ answer: string }>(`/datasets/${id}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  return answer;
}
