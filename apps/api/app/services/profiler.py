import pandas as pd


def get_dataset_profile(df: pd.DataFrame):

    missing_values = df.isnull().sum()

    missing_percentages = (
        missing_values / len(df) * 100
    ).round(2)

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "duplicates": int(df.duplicated().sum()),
        "column_names": list(df.columns),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "missing_values": missing_values.to_dict(),
        "missing_percentages": missing_percentages.to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict()
    }