import { useRef, useState, type DragEvent } from "react";

interface FileUploadProps {
  onFile: (file: File) => void;
  uploading: boolean;
  error: string | null;
}

const ACCEPTED = [".csv", ".xlsx"];

function isAccepted(file: File) {
  const name = file.name.toLowerCase();
  return ACCEPTED.some((ext) => name.endsWith(ext));
}

export default function FileUpload({ onFile, uploading, error }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  function handle(file: File | undefined) {
    if (!file) return;

    if (!isAccepted(file)) {
      setLocalError("Only CSV or Excel (.xlsx) files are supported.");
      return;
    }

    setLocalError(null);
    onFile(file);
  }

  function onDrop(event: DragEvent) {
    event.preventDefault();
    setDragging(false);
    handle(event.dataTransfer.files[0]);
  }

  const shownError = localError ?? error;

  return (
    <div>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        disabled={uploading}
        className={`flex w-full flex-col items-center justify-center gap-1 rounded-xl border-2 border-dashed px-6 py-8 text-center transition ${
          dragging
            ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950"
            : "border-slate-300 bg-white hover:border-indigo-400 dark:border-slate-700 dark:bg-slate-900"
        } disabled:cursor-wait disabled:opacity-60`}
      >
        <span className="text-2xl" aria-hidden>
          {uploading ? "⏳" : "📁"}
        </span>
        <span className="font-medium">
          {uploading ? "Uploading…" : "Drop a CSV or Excel file here, or click to browse"}
        </span>
        <span className="text-sm text-slate-500">Supported: .csv, .xlsx</span>
      </button>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED.join(",")}
        className="hidden"
        onChange={(e) => {
          handle(e.target.files?.[0]);
          e.target.value = "";
        }}
      />

      {shownError && (
        <p className="mt-2 text-sm text-rose-600 dark:text-rose-400">{shownError}</p>
      )}
    </div>
  );
}
