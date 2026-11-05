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

    column_profiles = {}
    for column in df.columns:
        series = df[column]
        non_null = series.dropna()
        detail = {
            "distinct": int(series.nunique(dropna=True)),
            "missing": int(series.isna().sum()),
            "sample_values": [str(value) for value in non_null.head(3).tolist()],
        }
        if pd.api.types.is_numeric_dtype(series) and not non_null.empty:
            detail["min"] = float(non_null.min())
            detail["max"] = float(non_null.max())
            detail["mean"] = float(non_null.mean())
        column_profiles[str(column)] = detail

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "duplicates": int(df.duplicated().sum()),
        "column_names": list(df.columns),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "missing_values": missing_values.to_dict(),
        "missing_percentages": missing_percentages.to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "column_profiles": column_profiles,
        "quality_warnings": [
            f"{column} has more than 25% missing values"
            for column, percent in missing_percentages.items() if percent > 25
        ],
    }
