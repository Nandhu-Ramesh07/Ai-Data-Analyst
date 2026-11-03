import pandas as pd

from app.agents.analyst import DataAnalystAgent

print("Starting test...")

agent = DataAnalystAgent()

print("Agent created")

df = pd.DataFrame({
    "product": ["A", "B", "C"],
    "sales": [120, 340, 90]
})

response = agent.ask(
    "Which product has the highest sales?",
    df
)

print("FINAL RESPONSE:")
print(response)
