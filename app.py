import streamlit as st
import pandas as pd

from services.data_loader import load_file
from services.profiler import get_dataset_profile
from agents.analyst import DataAnalystAgent


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# LOAD AGENT ONCE
# --------------------------------------------------

@st.cache_resource
def load_agent():

    agent = DataAnalystAgent()

    status = agent.warmup()

    return agent, status


agent, model_ready = load_agent()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📊 AI Data Analyst")

st.markdown(
    "Upload a dataset and ask questions using AI."
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

    if model_ready:
        st.success("🟢 Qwen3 Ready")
    else:
        st.error("🔴 Ollama Not Available")


# --------------------------------------------------
# DATASET SECTION
# --------------------------------------------------

if dataset_loaded:

    try:

        df = load_file(uploaded_file)

        profile = get_dataset_profile(df)

        st.subheader("📌 Dataset Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Rows", profile["rows"])
        col2.metric("Columns", profile["columns"])
        col3.metric("Duplicates", profile["duplicates"])

        st.subheader("👀 Dataset Preview")

        st.dataframe(
            df.head(),
            width="stretch"
        )

        numeric_df = df.select_dtypes(
            include=["number"]
        )

        if not numeric_df.empty:

            st.subheader("📈 Numerical Statistics")

            st.dataframe(
                numeric_df.describe(),
                width="stretch"
            )

        st.subheader("📋 Column Information")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### Numeric Columns")

            for col in profile["numeric_columns"]:
                st.markdown(f"- {col}")

        with col2:

            st.markdown("### Categorical Columns")

            for col in profile["categorical_columns"]:
                st.markdown(f"- {col}")

        st.subheader("🧹 Missing Values")

        missing_df = pd.DataFrame({
            "Column": list(profile["missing_values"].keys()),
            "Missing Count": list(profile["missing_values"].values()),
            "Missing %": list(profile["missing_percentages"].values())
        })

        st.dataframe(
            missing_df,
            width="stretch"
        )

        st.subheader("🔍 Data Types")

        dtype_df = pd.DataFrame({
            "Column": list(profile["dtypes"].keys()),
            "Data Type": list(profile["dtypes"].values())
        })

        st.dataframe(
            dtype_df,
            width="stretch"
        )

    except Exception as e:

        st.error(
            f"Dataset Error: {str(e)}"
        )

# --------------------------------------------------
# CHAT SECTION
# --------------------------------------------------

st.divider()

st.subheader("💬 Ask Your Data")

question = st.text_input(
    "Ask a question"
)

if st.button("Analyze"):

    if not model_ready:

        st.error(
            "Model is not available."
        )

    elif not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "🤖 Thinking..."
        ):

            try:

                response = agent.ask(
                            question,
                            df
                        )

                st.success(
                    response
                )

            except Exception as e:

                st.error(
                    f"AI Error: {str(e)}"
                )