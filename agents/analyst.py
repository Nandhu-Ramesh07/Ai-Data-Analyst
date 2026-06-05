from ollama import chat


class DataAnalystAgent:

    def __init__(self, model="qwen3:8b"):
        self.model = model

    def warmup(self):
        """
        Load model into memory.
        """
        try:
            chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Reply with OK"
                    }
                ]
            )
            return True

        except Exception:
            return False

    def ask(self, question, df):

        sample_data = df.head(5).to_string()

        prompt = f"""
You are an AI Data Analyst.

Dataset Information:

Rows: {df.shape[0]}
Columns: {list(df.columns)}

Sample Data:

{sample_data}

User Question:
{question}

Answer only using the dataset information provided.
"""

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]