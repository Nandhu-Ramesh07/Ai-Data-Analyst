import pandas as pd


def load_file(file_obj, filename):

    """Load a CSV or Excel file into a DataFrame."""

    file_name = filename.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(file_obj)

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(file_obj)

    else:
        raise ValueError(
            "Unsupported file format."
        )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace(" ", "_")
    )

    return df
