import { useEffect, useRef, useState, type FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { AnalysisResult } from "../api/client";
import AnalysisResultView from "./AnalysisResult";

export interface ChatMessage {
  role: "user" | "assistant" | "error";
  content: string;
  result?: AnalysisResult;
}

interface ChatPanelProps {
  messages: ChatMessage[];
  sending: boolean;
  onSend: (question: string) => void;
}

const bubbleClasses: Record<ChatMessage["role"], string> = {
  user: "ml-auto bg-indigo-600 text-white",
  assistant: "bg-slate-100 dark:bg-slate-800",
  error: "bg-rose-50 text-rose-800 ring-1 ring-rose-200 dark:bg-rose-950 dark:text-rose-200 dark:ring-rose-900",
};

export default function ChatPanel({ messages, sending, onSend }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages, sending]);

  function submit(event: FormEvent) {
    event.preventDefault();

    const question = input.trim();
    if (!question || sending) return;

    onSend(question);
    setInput("");
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex max-h-[28rem] min-h-32 flex-col gap-3 overflow-y-auto">
        {messages.length === 0 && !sending && (
          <p className="text-sm text-slate-500">
            Ask anything about your dataset, e.g. “Which column has the most missing values?”
          </p>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${bubbleClasses[message.role]}`}
          >
            {message.role === "assistant" ? (
              <div className="markdown">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                {message.result && <AnalysisResultView result={message.result} />}
              </div>
            ) : (
              <p className="whitespace-pre-wrap">{message.content}</p>
            )}
          </div>
        ))}

        {sending && (
          <div className="max-w-[85%] animate-pulse rounded-2xl bg-slate-100 px-4 py-2.5 text-slate-500 dark:bg-slate-800">
            🤖 Analyzing dataset…
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <form onSubmit={submit} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your dataset..."
          className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 dark:border-slate-700 dark:bg-slate-950 dark:focus:ring-indigo-900"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
