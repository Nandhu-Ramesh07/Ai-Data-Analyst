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

    def ask(self, question: str):

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return response["message"]["content"]   