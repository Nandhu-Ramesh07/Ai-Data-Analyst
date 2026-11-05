import pandas as pd
from typing import TypedDict


class AgentState(TypedDict):
    question: str
    df: pd.DataFrame
    profile: dict
    method: str
    result: dict
