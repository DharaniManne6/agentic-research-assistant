# Agentic Research & Report Assistant

A multi-step, tool-using AI agent built with **LangGraph** and **LangChain**, capable of searching the web, retrieving live news, performing calculations, maintaining conversational memory across turns, and reasoning over multi-tool results — with full observability via **LangSmith** tracing. Includes a deployed **Streamlit** chat UI.

This project demonstrates core patterns used in production agentic AI systems: ReAct-style reasoning, dynamic tool selection, stateful multi-turn conversation, and debugging/evaluating LLM behavior through tracing.

🔗 **Live Demo**: [https://your-app-name.streamlit.app](https://your-app-name.streamlit.app)

---

## Features

- **ReAct-style agent** built with LangGraph's `create_agent`, which reasons step-by-step, decides when to call tools, observes results, and produces a final answer.
- **Multiple tools**:
  - `web_search` — general-purpose web search (DuckDuckGo) for facts, definitions, and how-to information.
  - `news_search` — real-time news search for current events, stock updates, and "latest" queries.
  - `calculator` — safe arithmetic evaluation, offloading math from the LLM.
- **Conversational memory** via LangGraph's `InMemorySaver` checkpointer — the agent remembers prior turns within a session and can answer follow-up questions (e.g., comparisons) without re-searching.
- **Retry logic** to gracefully handle occasional tool-call formatting errors from the LLM provider.
- **LangSmith tracing** — every agent run is logged with full visibility into reasoning steps, tool calls, inputs/outputs, and latency.
- **Streamlit chat UI** — deployed publicly via Streamlit Community Cloud, with conversation history, a "Clear conversation" button, and an info sidebar.

---

## Architecture

```
User Input
    │
    ▼
┌─────────────────────┐
│   LangGraph Agent    │◄──────────────┐
│ (Llama 3.3 70B via   │                │
│  Groq, temperature=0)│                │
└─────────┬────────────┘                │
          │                             │
          ▼                             │
   Decides: respond directly,           │
   or call a tool?                      │
          │                             │
   ┌──────┴──────┬───────────────┐      │
   ▼              ▼               ▼     │
web_search    news_search     calculator│
   │              │               │     │
   └──────┬───────┴───────┬───────┘     │
          ▼               │             │
   Tool result returned ──┴─────────────┘
          │
          ▼
   Final answer (with memory persisted
   via InMemorySaver checkpointer)
```

All steps are logged to **LangSmith** for tracing and debugging.

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent framework | LangGraph (`create_agent`, ReAct pattern) |
| LLM | Llama 3.3 70B (via Groq API — free tier) |
| Tools | DuckDuckGo Search (`ddgs`), custom calculator tool |
| Memory | LangGraph `InMemorySaver` checkpointer |
| Observability | LangSmith tracing |
| UI / Deployment | Streamlit + Streamlit Community Cloud |
| Language | Python 3.14 |

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd agentic-research-assistant
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your keys:

```
GROQ_API_KEY=your_groq_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=agentic-research-assistant
```

- Get a free Groq API key at [console.groq.com](https://console.groq.com)
- Get a free LangSmith API key at [smith.langchain.com](https://smith.langchain.com)

### 4. Run the agent

CLI version:
```bash
python main.py
```

Streamlit chat UI (local):
```bash
streamlit run app.py
```

---

## Deployment

The Streamlit UI is deployed for free on **Streamlit Community Cloud**:

1. Push the repo to GitHub (excluding `.env`, which is gitignored).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing to this repo, branch `main`, file `app.py`.
3. Add the same environment variables from `.env.example` as **Secrets** in the app's settings (Groq and LangSmith API keys).
4. Deploy — Streamlit Cloud builds the app from `requirements.txt` and serves it at a public URL.

---

## Example Interaction

```
=== Research & Report Agent ===
Type 'exit' to quit.

You: What's the latest news on Nvidia?
Agent: The latest news on Nvidia includes:
- Nvidia has begun sales pitches for its new "Vera" CPUs for AI data centers to Chinese clients...
- Analysts are hiking Nvidia's forecast revenue and price targets...
(sourced from Reuters, UPI, Mint, Barchart — published June 12-13, 2026)

You: What about AMD instead?
Agent: The latest news on AMD includes:
- AMD stock could surge past $665 on explosive data center demand...
- Citi has upgraded AMD stock, with analysts remaining bullish...
(sourced from MSN, Barchart, StockStory.org, TheStreet)

You: Which of the two seems to have better momentum based on what you found?
Agent: Based on the news articles I found, AMD seems to have better momentum.
AMD stock has rallied significantly over the past three months, surging more
than 125%, with a recent upgrade from Citi. In contrast, Nvidia appears to be
cooling from its recent highs...
```

This third turn demonstrates **contextual reasoning over conversation memory** — the agent correctly resolved "the two" to Nvidia and AMD from earlier turns without re-searching.

---

## Project Structure

```
agentic-research-assistant/
├── agent.py            # Agent definition: LLM, tools, system prompt, memory
├── tools.py            # Tool definitions: web_search, news_search, calculator
├── main.py             # CLI entry point with retry logic
├── app.py              # Streamlit chat UI (deployed)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Challenges & Learnings

A key part of this project was iteratively debugging real agent behavior rather than assuming it would "just work":

- **Tool-call format instability**: `llama-3.3-70b-versatile` occasionally produced malformed function-call syntax via Groq, causing `tool_use_failed` errors. Resolved with a retry wrapper around the agent invocation.
- **Search relevance**: General-purpose web search returned homepage descriptions rather than actual news content for "latest news" queries. Solved by adding a dedicated `news_search` tool using DuckDuckGo's news endpoint, which returns dated headlines and snippets.
- **Model size vs. contextual reasoning**: Testing with `llama-3.1-8b-instant` (faster, cheaper) revealed a recurring failure mode — on ambiguous follow-up questions (e.g., "which of the two..."), the smaller model would call a search tool with an unrelated query and confidently answer based on irrelevant results (e.g., answering about Ford/Tesla or Tesla/Rivian when the actual prior topic was Nvidia/AMD). Switching to `llama-3.3-70b-versatile` with a stricter system prompt resolved this, correctly resolving references to earlier conversation turns without unnecessary tool calls.
- **Observability**: Adding LangSmith tracing made these failure modes visible and debuggable — each run can be inspected step-by-step (reasoning, tool calls, inputs/outputs, latency), which was essential for diagnosing the issues above.

---

## Possible Extensions

- Add a custom `StateGraph` (instead of the prebuilt `create_agent`) to demonstrate finer-grained control over the reasoning loop.
- Add persistent memory (e.g., SQLite-backed checkpointer) instead of in-memory, so conversations survive app restarts.
- Add evaluation datasets in LangSmith to systematically benchmark model/prompt changes.
- Add streaming responses in the Streamlit UI for a more responsive feel.
