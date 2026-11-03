from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from app.serialize import frame_to_table, to_native
from app.services.data_loader import load_file
from app.services.profiler import get_dataset_profile
from app.store import add_dataset, get_dataset


router = APIRouter(prefix="/datasets")


class ChatRequest(BaseModel):
    question: str


def build_payload(dataset_id: str, entry: dict) -> dict:

    df = entry["df"]

    numeric_df = df.select_dtypes(include=["number"])

    return {
        "id": dataset_id,
        "filename": entry["filename"],
        "profile": to_native(get_dataset_profile(df)),
        "preview": frame_to_table(df.head()),
        "numeric_stats": (
            None
            if numeric_df.empty
            else frame_to_table(numeric_df.describe(), include_index=True)
        )
    }


def require_dataset(dataset_id: str) -> dict:

    entry = get_dataset(dataset_id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return entry


@router.post("")
async def upload_dataset(file: UploadFile):

    filename = file.filename or ""

    try:
        df = await run_in_threadpool(load_file, file.file, filename)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {e}")

    dataset_id = add_dataset(df, filename)

    return build_payload(dataset_id, require_dataset(dataset_id))


@router.get("/{dataset_id}")
def read_dataset(dataset_id: str):

    return build_payload(dataset_id, require_dataset(dataset_id))


@router.post("/{dataset_id}/chat")
async def chat_with_dataset(dataset_id: str, body: ChatRequest, request: Request):

    entry = require_dataset(dataset_id)

    question = body.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question is empty")

    agent = request.app.state.agent

    try:
        answer = await run_in_threadpool(agent.ask, question, entry["df"])

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI Error: {e}")

    return {"answer": answer}
