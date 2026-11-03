import uuid
from threading import Lock

import pandas as pd


# In-memory dataset store. Datasets are lost when the API restarts.
_datasets: dict[str, dict] = {}
_lock = Lock()


def add_dataset(df: pd.DataFrame, filename: str) -> str:
    dataset_id = uuid.uuid4().hex

    with _lock:
        _datasets[dataset_id] = {
            "df": df,
            "filename": filename
        }

    return dataset_id


def get_dataset(dataset_id: str) -> dict | None:
    with _lock:
        return _datasets.get(dataset_id)
