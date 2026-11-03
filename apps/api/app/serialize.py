import math

import numpy as np
import pandas as pd


def to_native(value):

    """Convert numpy / pandas scalars to JSON-safe Python values."""

    if isinstance(value, dict):
        return {str(k): to_native(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_native(v) for v in value]

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None

    if value is pd.NaT or (not isinstance(value, (str, bytes)) and pd.api.types.is_scalar(value) and pd.isna(value)):
        return None

    if isinstance(value, (pd.Timestamp, pd.Timedelta)):
        return str(value)

    return value


def frame_to_table(df: pd.DataFrame, include_index: bool = False) -> dict:

    """Serialize a DataFrame into {columns, rows} with NaN -> None."""

    if include_index:
        df = df.reset_index(names="")

    return {
        "columns": [str(c) for c in df.columns],
        "rows": [
            [to_native(v) for v in row]
            for row in df.itertuples(index=False, name=None)
        ]
    }
