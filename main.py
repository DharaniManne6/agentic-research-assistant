from agent import agent
from groq import BadRequestError
import time

def main():
    print("=== Research & Report Agent ===")
    print("Type 'exit' to quit.\n")

    config = {"configurable": {"thread_id": "session-1"}}

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        for attempt in range(3):
            try:
                result = agent.invoke({"messages": [("user", user_input)]}, config)
                response = result["messages"][-1].content
                print(f"\nAgent: {response}\n")
                break
            except BadRequestError as e:
                print(f"(Retrying due to a tool-call formatting hiccup... attempt {attempt + 1})")
                time.sleep(1)
        else:
            print("\nAgent: Sorry, I had trouble processing that. Could you rephrase?\n")

if __name__ == "__main__":
    main()