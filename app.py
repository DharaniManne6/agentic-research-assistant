import streamlit as st
import os

# Bridge Streamlit secrets into environment variables (for Streamlit Cloud)
for key in ["GROQ_API_KEY", "LANGSMITH_TRACING", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT"]:
    if key in st.secrets:
        os.environ[key] = st.secrets[key]

from agent import agent
from groq import BadRequestError, APIError
import time
import uuid

st.set_page_config(page_title="Agentic Research Assistant", page_icon="🔎", layout="centered")

st.title("🔎 Agentic Research Assistant")
st.caption("Multi-tool AI agent with web search, news search, calculator, and memory — built with LangGraph + Groq")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask me anything — news, facts, or calculations...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get agent response
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = None
            last_error = None
            for attempt in range(5):
                try:
                    result = agent.invoke({"messages": [("user", user_input)]}, config)
                    response = result["messages"][-1].content
                    break
                except (BadRequestError, APIError) as e:
                    last_error = e
                    time.sleep(1)
            if response is None:
                response = "Sorry, I had trouble processing that. Could you rephrase?"
                if last_error:
                    st.caption(f"(Debug: {type(last_error).__name__} - {last_error})")

            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown(
        "This agent can:\n"
        "- 🔍 Search the web for general info\n"
        "- 📰 Search for latest news\n"
        "- 🧮 Do calculations\n"
        "- 🧠 Remember context across turns\n\n"
        "Built with **LangGraph**, **Groq (Llama 3.3 70B)**, and traced with **LangSmith**."
    )
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()