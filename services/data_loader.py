import pandas as pd


def load_file(uploaded_file):

    """Load a CSV or Excel file into a DataFrame."""

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)

    else:
        raise ValueError(
            "Unsupported file format."
        )

    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
    )

    return df