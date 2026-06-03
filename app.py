import streamlit as st

from services.data_loader import load_file
from services.profiler import get_dataset_profile


st.set_page_config(
    page_title="AI Data Analyst",
    layout="wide"
)

st.title("📊 AI Data Analyst")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

if uploaded_file:

    df = load_file(uploaded_file)

    st.success("Dataset loaded successfully!")

    st.subheader("Preview")

    st.dataframe(df.head())

    profile = get_dataset_profile(df)

    st.subheader("Dataset Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", profile["rows"])
    col2.metric("Columns", profile["columns"])
    col3.metric("Duplicates", profile["duplicates"])

    st.subheader("Columns")

    st.write(profile["column_names"])

    st.subheader("Missing Values")

    st.json(profile["missing_values"])