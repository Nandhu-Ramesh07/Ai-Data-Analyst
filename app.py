import streamlit as st
import pandas as pd

from services.data_loader import load_file
from services.profiler import get_dataset_profile


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📊 AI Data Analyst")
st.markdown(
    "Upload a CSV or Excel file and explore your data."
)

# --------------------------------------------------
# FILE UPLOADER
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

dataset_loaded = uploaded_file is not None

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("Project Status")

    if dataset_loaded:
        st.success("✅ Dataset Loaded")
    else:
        st.info("📂 No dataset uploaded")

    st.divider()

    st.header("AI Status")

    st.warning("⏳ AI Model Not Connected")

# --------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------

if dataset_loaded:

    try:

        df = load_file(uploaded_file)

        profile = get_dataset_profile(df)

        # ------------------------------------------
        # METRICS
        # ------------------------------------------

        st.subheader("📌 Dataset Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Rows", profile["rows"])
        col2.metric("Columns", profile["columns"])
        col3.metric("Duplicates", profile["duplicates"])

        # ------------------------------------------
        # PREVIEW
        # ------------------------------------------

        st.subheader("👀 Dataset Preview")

        st.dataframe(
            df.head(),
            width="stretch"
        )

        # ------------------------------------------
        # STATISTICS
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
        # COLUMN INFO
        # ------------------------------------------

        st.subheader("📋 Column Information")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### Numeric Columns")

            if profile["numeric_columns"]:
                for col in profile["numeric_columns"]:
                    st.markdown(f"- {col}")
            else:
                st.info("No numeric columns")

        with col2:

            st.markdown("### Categorical Columns")

            if profile["categorical_columns"]:
                for col in profile["categorical_columns"]:
                    st.markdown(f"- {col}")
            else:
                st.info("No categorical columns")

        # ------------------------------------------
        # MISSING VALUES
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
        # DATA TYPES
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

        # ------------------------------------------
        # CHAT PLACEHOLDER
        # ------------------------------------------

        st.divider()

        st.subheader("💬 Ask Your Data")

        question = st.text_input(
            "Ask a question about your dataset"
        )

        if st.button("Analyze"):

            if question.strip():

                st.info(
                    f"You asked: {question}"
                )

            else:

                st.warning(
                    "Please enter a question."
                )

    except Exception as e:

        st.error(
            f"Error loading dataset: {str(e)}"
        )

else:

    st.info(
        "👆 Upload a CSV or Excel file to begin analysis."
    )