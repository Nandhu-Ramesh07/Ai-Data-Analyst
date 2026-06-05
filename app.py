import streamlit as st
import pandas as pd

from services.data_loader import load_file
from services.profiler import get_dataset_profile
from agents.analyst import DataAnalystAgent


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# LOAD AGENT ONCE
# ==================================================

@st.cache_resource
def load_agent():
    agent = DataAnalystAgent()

    try:
        model_ready = agent.warmup()
    except Exception:
        model_ready = False

    return agent, model_ready


agent, model_ready = load_agent()


# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_file" not in st.session_state:
    st.session_state.current_file = None


# ==================================================
# HEADER
# ==================================================

st.title("📊 AI Data Analyst")
st.markdown(
    "Upload a dataset and ask questions using AI."
)


# ==================================================
# FILE UPLOADER
# ==================================================

uploaded_file = st.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

dataset_loaded = uploaded_file is not None


# ==================================================
# RESET CHAT WHEN NEW FILE IS UPLOADED
# ==================================================

if uploaded_file is not None:

    if st.session_state.current_file != uploaded_file.name:

        st.session_state.messages = []
        st.session_state.current_file = uploaded_file.name


# ==================================================
# SIDEBAR
# ==================================================

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

    st.divider()

    if dataset_loaded:
        st.header("Dataset")

        st.write(
            f"**File:** {uploaded_file.name}"
        )


# ==================================================
# MAIN APPLICATION
# ==================================================

if dataset_loaded:

    try:

        # ------------------------------------------
        # LOAD DATA
        # ------------------------------------------

        df = load_file(uploaded_file)

        profile = get_dataset_profile(df)

        # ==========================================
        # CHAT SECTION
        # ==========================================

        st.subheader("💬 Ask Your Data")

        for message in st.session_state.messages:

            with st.chat_message(
                message["role"]
            ):
                st.markdown(
                    message["content"]
                )

        prompt = st.chat_input(
            "Ask a question about your dataset..."
        )

        if prompt:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):

                with st.spinner(
                    "🤖 Analyzing dataset..."
                ):

                    try:

                        response = agent.ask(
                            prompt,
                            df
                        )

                        st.markdown(response)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response
                            }
                        )

                    except Exception as e:

                        error_message = (
                            f"AI Error: {str(e)}"
                        )

                        st.error(error_message)

        st.divider()

        # ==========================================
        # DATASET SUMMARY
        # ==========================================

        st.subheader("📌 Dataset Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Rows",
            profile["rows"]
        )

        col2.metric(
            "Columns",
            profile["columns"]
        )

        col3.metric(
            "Duplicates",
            profile["duplicates"]
        )

        # ==========================================
        # DATA PREVIEW
        # ==========================================

        st.subheader("👀 Dataset Preview")

        st.dataframe(
            df.head(),
            width="stretch"
        )

        # ==========================================
        # NUMERICAL STATISTICS
        # ==========================================

        numeric_df = df.select_dtypes(
            include=["number"]
        )

        if not numeric_df.empty:

            st.subheader(
                "📈 Numerical Statistics"
            )

            st.dataframe(
                numeric_df.describe(),
                width="stretch"
            )

        # ==========================================
        # COLUMN INFORMATION
        # ==========================================

        st.subheader(
            "📋 Column Information"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                "### Numeric Columns"
            )

            if profile["numeric_columns"]:

                for col in profile[
                    "numeric_columns"
                ]:
                    st.markdown(
                        f"- {col}"
                    )

            else:
                st.info(
                    "No numeric columns"
                )

        with col2:

            st.markdown(
                "### Categorical Columns"
            )

            if profile[
                "categorical_columns"
            ]:

                for col in profile[
                    "categorical_columns"
                ]:
                    st.markdown(
                        f"- {col}"
                    )

            else:
                st.info(
                    "No categorical columns"
                )

        # ==========================================
        # MISSING VALUES
        # ==========================================

        st.subheader(
            "🧹 Missing Values"
        )

        missing_df = pd.DataFrame({
            "Column":
                list(
                    profile[
                        "missing_values"
                    ].keys()
                ),
            "Missing Count":
                list(
                    profile[
                        "missing_values"
                    ].values()
                ),
            "Missing %":
                list(
                    profile[
                        "missing_percentages"
                    ].values()
                )
        })

        missing_df = missing_df.sort_values(
            by="Missing %",
            ascending=False
        )

        st.dataframe(
            missing_df,
            width="stretch"
        )

        # ==========================================
        # DATA TYPES
        # ==========================================

        st.subheader(
            "🔍 Data Types"
        )

        dtype_df = pd.DataFrame({
            "Column":
                list(
                    profile[
                        "dtypes"
                    ].keys()
                ),
            "Data Type":
                list(
                    profile[
                        "dtypes"
                    ].values()
                )
        })

        st.dataframe(
            dtype_df,
            width="stretch"
        )

    except Exception as e:

        st.error(
            f"Dataset Error: {str(e)}"
        )

else:

    st.info(
        "👆 Upload a CSV or Excel file to begin analysis."
    )