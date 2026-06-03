import streamlit as st
import pandas as pd

from services.data_loader import load_file
from services.profiler import get_dataset_profile


# --------------------------------------------------
# Page Config
# --------------------------------------------------

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("📊 AI Data Analyst")
st.markdown(
    "Upload a CSV or Excel file and explore your data."
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("Project Status")

    if "dataset_loaded" not in st.session_state:
        st.info("No dataset uploaded")
    else:
        st.success("Dataset Loaded")


# --------------------------------------------------
# File Upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)


# --------------------------------------------------
# Main App
# --------------------------------------------------

if uploaded_file:

    try:

        df = load_file(uploaded_file)

        st.session_state["dataset_loaded"] = True

        profile = get_dataset_profile(df)

        # ------------------------------------------
        # Metrics
        # ------------------------------------------

        st.subheader("📌 Dataset Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Rows", profile["rows"])

        with col2:
            st.metric("Columns", profile["columns"])

        with col3:
            st.metric("Duplicates", profile["duplicates"])

        # ------------------------------------------
        # Preview
        # ------------------------------------------

        st.subheader("👀 Dataset Preview")

        st.dataframe(
            df.head(),
            width="stretch"
        )

        # ------------------------------------------
        # Statistics
        # ------------------------------------------

        numeric_df = df.select_dtypes(
            include=["number"]
        )

        if not numeric_df.empty:

            st.subheader("📈 Numerical Statistics")

            st.dataframe(
                numeric_df.describe(),
                width="stretch"
            )

        # ------------------------------------------
        # Column Information
        # ------------------------------------------

        st.subheader("📋 Column Information")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### Numeric Columns")

            if profile["numeric_columns"]:
                st.write(profile["numeric_columns"])
            else:
                st.info("No numeric columns found")

        with col2:

            st.markdown("### Categorical Columns")

            if profile["categorical_columns"]:
                st.write(profile["categorical_columns"])
            else:
                st.info("No categorical columns found")

        # ------------------------------------------
        # Missing Values
        # ------------------------------------------

        missing_df = pd.DataFrame({
            "Column": list(profile["missing_values"].keys()),
            "Missing Count": list(profile["missing_values"].values()),
            "Missing %": list(profile["missing_percentages"].values())
        })

        missing_df = missing_df.sort_values(
            by="Missing %",
            ascending=False
        )

        st.subheader("🧹 Missing Values")

        st.dataframe(
            missing_df,
            width="stretch"
        )

        # ------------------------------------------
        # Data Types
        # ------------------------------------------

        dtype_df = pd.DataFrame({
            "Column": list(profile["dtypes"].keys()),
            "Data Type": list(profile["dtypes"].values())
        })

        st.subheader("🔍 Data Types")

        st.dataframe(
            dtype_df,
            width="stretch"
        )

    except Exception as e:

        st.error(
            f"Error loading dataset: {str(e)}"
        )

else:

    st.info(
        "👆 Upload a CSV or Excel file to begin analysis."
    )