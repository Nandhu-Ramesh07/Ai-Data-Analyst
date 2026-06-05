from agents.analyst import DataAnalystAgent

print("Starting test...")

agent = DataAnalystAgent()

print("Agent created")

response = agent.ask(
    "What is machine learning?"
)

print("FINAL RESPONSE:")
print(response)