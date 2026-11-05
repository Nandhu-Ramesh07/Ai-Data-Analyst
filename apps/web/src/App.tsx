import { useEffect, useMemo, useState } from "react";

import {
  askQuestion,
  downloadReport,
  getConversationMessages,
  getConversations,
  getDataset,
  getHealth,
  uploadDataset,
  type Dataset,
  type Conversation,
  type Health,
  type Table,
} from "./api/client";
import ChatPanel, { type ChatMessage } from "./components/ChatPanel";
import ColumnLists from "./components/ColumnLists";
import DataTable from "./components/DataTable";
import FileUpload from "./components/FileUpload";
import Section from "./components/Section";
import StatusSidebar from "./components/StatusSidebar";
import SummaryCards from "./components/SummaryCards";

const DATASET_KEY = "ai-data-analyst:dataset-id";

function readStoredId(): string | null {
  try {
    return sessionStorage.getItem(DATASET_KEY);
  } catch {
    return null;
  }
}

function storeId(id: string | null) {
  try {
    if (id) sessionStorage.setItem(DATASET_KEY, id);
    else sessionStorage.removeItem(DATASET_KEY);
  } catch {
    // storage unavailable; the dataset just won't survive a refresh
  }
}

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [apiOnline, setApiOnline] = useState(true);
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [conversations, setConversations] = useState<Conversation[]>([]);

  // Poll health until the model warmup has finished (or the API comes back)
  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;

    async function poll() {
      try {
        const result = await getHealth();
        if (cancelled) return;

        setHealth(result);
        setApiOnline(true);

        if (result.model_ready !== null) return;
      } catch {
        if (cancelled) return;
        setApiOnline(false);
      }

      timer = window.setTimeout(poll, 3000);
    }

    poll();

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, []);

  // Restore the dataset after a page refresh
  useEffect(() => {
    const id = readStoredId();
    if (!id) return;

    getDataset(id)
      .then(setDataset)
      .catch(() => storeId(null));
  }, []);

  async function handleFile(file: File) {
    setUploading(true);
    setUploadError(null);

    try {
      const result = await uploadDataset(file);
      setDataset(result);
      setMessages([]);
      setConversationId(undefined);
      setConversations([]);
      storeId(result.id);
    } catch (error) {
      setUploadError(`Dataset Error: ${(error as Error).message}`);
    } finally {
      setUploading(false);
    }
  }

  useEffect(() => {
    if (!dataset) return;
    getConversations(dataset.id).then(setConversations).catch(() => setConversations([]));
  }, [dataset?.id]);

  async function selectConversation(id: string) {
    if (!dataset || !id) { setConversationId(undefined); setMessages([]); return; }
    const restored = await getConversationMessages(dataset.id, id);
    setConversationId(id);
    setMessages(restored.map((message) => ({ role: message.role, content: message.content, result: message.result })));
  }

  async function handleSend(question: string) {
    if (!dataset) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setSending(true);

    try {
      const result = await askQuestion(dataset.id, question, conversationId);
      setConversationId(result.conversation_id);
      getConversations(dataset.id).then(setConversations).catch(() => undefined);
      setMessages((prev) => [...prev, { role: "assistant", content: result.message, result }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: "error", content: (error as Error).message }]);
    } finally {
      setSending(false);
    }
  }

  const missingTable = useMemo<Table | null>(() => {
    if (!dataset) return null;

    const { missing_values, missing_percentages } = dataset.profile;

    const rows = Object.keys(missing_values)
      .map((column) => [column, missing_values[column], missing_percentages[column] ?? 0] as const)
      .sort((a, b) => b[2] - a[2])
      .map((row) => [...row]);

    return { columns: ["Column", "Missing Count", "Missing %"], rows };
  }, [dataset]);

  const dtypeTable = useMemo<Table | null>(() => {
    if (!dataset) return null;

    return {
      columns: ["Column", "Data Type"],
      rows: Object.entries(dataset.profile.dtypes),
    };
  }, [dataset]);

  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      <StatusSidebar health={health} apiOnline={apiOnline} filename={dataset?.filename ?? null} />

      <main className="mx-auto flex w-full max-w-6xl flex-col gap-6 p-4 sm:p-8">
        <header>
          <h1 className="text-3xl font-bold">📊 AI Data Analyst</h1>
          <p className="mt-1 text-slate-500">Upload a dataset and ask questions using AI.</p>
        </header>

        <FileUpload onFile={handleFile} uploading={uploading} error={uploadError} />

        {dataset && missingTable && dtypeTable ? (
          <>
            <Section title="Ask Your Data" icon="💬">
              <div className="mb-3 flex flex-wrap justify-between gap-2"><select value={conversationId ?? ""} onChange={(event) => selectConversation(event.target.value)} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:bg-slate-900"><option value="">New conversation</option>{conversations.map((conversation) => <option value={conversation.id} key={conversation.id}>{conversation.title}</option>)}</select><button onClick={() => downloadReport(dataset.id, conversationId).catch((error) => setUploadError(error.message))} className="rounded-lg bg-slate-800 px-3 py-2 text-sm font-medium text-white">Download PDF report</button></div>
              <ChatPanel messages={messages} sending={sending} onSend={handleSend} />
            </Section>

            <Section title="Dataset Summary" icon="📌">
              <SummaryCards profile={dataset.profile} />
              {dataset.profile.quality_warnings && dataset.profile.quality_warnings.length > 0 && <ul className="mt-4 list-disc pl-5 text-sm text-amber-700 dark:text-amber-300">{dataset.profile.quality_warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>}
            </Section>

            <Section title="Dataset Preview" icon="👀">
              <DataTable table={dataset.preview} />
            </Section>

            {dataset.numeric_stats && (
              <Section title="Numerical Statistics" icon="📈">
                <DataTable table={dataset.numeric_stats} />
              </Section>
            )}

            <Section title="Column Information" icon="📋">
              <ColumnLists profile={dataset.profile} />
            </Section>

            <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
              <Section title="Missing Values" icon="🧹">
                <DataTable table={missingTable} />
              </Section>

              <Section title="Data Types" icon="🔍">
                <DataTable table={dtypeTable} />
              </Section>
            </div>
          </>
        ) : (
          <div className="rounded-xl bg-sky-50 px-5 py-4 text-sky-800 ring-1 ring-sky-200 dark:bg-sky-950 dark:text-sky-200 dark:ring-sky-900">
            👆 Upload a CSV or Excel file to begin analysis.
          </div>
        )}
      </main>
    </div>
  );
}
