import pandas as pd
from typing import TypedDict


class AgentState(TypedDict):
    question : str
    df : pd.DataFrame
    pandas_code : str
    result : str
    response : str    