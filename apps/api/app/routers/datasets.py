from pathlib import Path
import uuid

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.config import DATA_DIR, MAX_UPLOAD_BYTES
from app.graph.workflow import build_workflow
from app.serialize import frame_to_table, to_native
from app.services.data_loader import load_file
from app.services.profiler import get_dataset_profile
from app.services.reports import build_report
from app.store import add_dataset, add_message, create_conversation, get_dataset, get_messages, list_conversations

router = APIRouter(prefix="/datasets")
workflow = build_workflow()


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class ConversationRequest(BaseModel):
    title: str = Field(default="New analysis", max_length=256)


def build_payload(dataset_id: str, entry: dict) -> dict:
    df = entry["df"]
    numeric_df = df.select_dtypes(include=["number"])
    return {"id": dataset_id, "filename": entry["filename"], "profile": entry["profile"], "preview": frame_to_table(df.head()), "numeric_stats": None if numeric_df.empty else frame_to_table(numeric_df.describe(), include_index=True)}


def require_dataset(dataset_id: str) -> dict:
    entry = get_dataset(dataset_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return entry


@router.post("")
async def upload_dataset(file: UploadFile):
    filename = Path(file.filename or "").name
    if not filename.lower().endswith((".csv", ".xlsx", ".parquet")):
        raise HTTPException(status_code=400, detail="Supported formats are CSV, XLSX, and Parquet")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination = DATA_DIR / f"upload-{uuid.uuid4().hex}{Path(filename).suffix.lower()}"
    size = 0
    try:
        with destination.open("wb") as target:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Upload exceeds the configured size limit")
                target.write(chunk)
        with destination.open("rb") as source:
            df = await run_in_threadpool(load_file, source, filename)
        profile = to_native(get_dataset_profile(df))
        dataset_id = add_dataset(df, filename, destination, profile)
        return build_payload(dataset_id, require_dataset(dataset_id))
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise
    except Exception as error:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Could not read file: {error}")


@router.get("/{dataset_id}")
def read_dataset(dataset_id: str):
    return build_payload(dataset_id, require_dataset(dataset_id))


@router.get("/{dataset_id}/conversations")
def conversations(dataset_id: str):
    require_dataset(dataset_id)
    return list_conversations(dataset_id)


@router.post("/{dataset_id}/conversations")
def new_conversation(dataset_id: str, body: ConversationRequest):
    require_dataset(dataset_id)
    return create_conversation(dataset_id, body.title)


@router.get("/{dataset_id}/conversations/{conversation_id}")
def conversation_messages(dataset_id: str, conversation_id: str):
    require_dataset(dataset_id)
    return get_messages(conversation_id)


@router.post("/{dataset_id}/chat")
async def chat_with_dataset(dataset_id: str, body: ChatRequest):
    entry = require_dataset(dataset_id)
    question = body.question.strip()
    conversation_id = body.conversation_id or create_conversation(dataset_id, question[:80])["id"]
    try:
        state = await run_in_threadpool(workflow.invoke, {"question": question, "df": entry["df"], "profile": entry["profile"]})
        payload = to_native({"conversation_id": conversation_id, "method": state["method"], **state["result"]})
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Analysis Error: {error}")
    add_message(conversation_id, "user", question)
    add_message(conversation_id, "assistant", payload["message"], payload)
    return payload


@router.post("/{dataset_id}/reports")
def report(dataset_id: str, conversation_id: str | None = None):
    entry = require_dataset(dataset_id)
    pdf = build_report(entry["filename"], entry["profile"], get_messages(conversation_id) if conversation_id else [])
    safe_name = Path(entry["filename"]).stem
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{safe_name}-analysis-report.pdf"'})
