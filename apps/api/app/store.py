import uuid
from pathlib import Path

import pandas as pd
from sqlalchemy import select

from app.database import SessionLocal
from app.models import ConversationRecord, DatasetRecord, MessageRecord
from app.services.data_loader import load_file

_cache: dict[str, pd.DataFrame] = {}


def add_dataset(df: pd.DataFrame, filename: str, storage_path: Path, profile: dict) -> str:
    dataset_id = uuid.uuid4().hex
    with SessionLocal.begin() as session:
        session.add(DatasetRecord(id=dataset_id, filename=filename, storage_path=str(storage_path), profile=profile))
    _cache[dataset_id] = df
    return dataset_id


def get_dataset(dataset_id: str) -> dict | None:
    with SessionLocal() as session:
        record = session.get(DatasetRecord, dataset_id)
        if record is None:
            return None
        if dataset_id not in _cache:
            with open(record.storage_path, "rb") as source:
                _cache[dataset_id] = load_file(source, record.filename)
        return {"df": _cache[dataset_id], "filename": record.filename, "profile": record.profile, "storage_path": record.storage_path}


def create_conversation(dataset_id: str, title: str = "New analysis") -> dict:
    conversation_id = uuid.uuid4().hex
    with SessionLocal.begin() as session:
        session.add(ConversationRecord(id=conversation_id, dataset_id=dataset_id, title=title))
    return {"id": conversation_id, "dataset_id": dataset_id, "title": title}


def list_conversations(dataset_id: str) -> list[dict]:
    with SessionLocal() as session:
        records = session.scalars(select(ConversationRecord).where(ConversationRecord.dataset_id == dataset_id).order_by(ConversationRecord.created_at.desc())).all()
        return [{"id": item.id, "dataset_id": item.dataset_id, "title": item.title, "created_at": item.created_at.isoformat() if item.created_at else None} for item in records]


def get_messages(conversation_id: str) -> list[dict]:
    with SessionLocal() as session:
        records = session.scalars(select(MessageRecord).where(MessageRecord.conversation_id == conversation_id).order_by(MessageRecord.created_at)).all()
        return [{"id": item.id, "role": item.role, "content": item.content, "result": item.result, "created_at": item.created_at.isoformat() if item.created_at else None} for item in records]


def add_message(conversation_id: str, role: str, content: str, result: dict | None = None) -> None:
    with SessionLocal.begin() as session:
        session.add(MessageRecord(id=uuid.uuid4().hex, conversation_id=conversation_id, role=role, content=content, result=result))
