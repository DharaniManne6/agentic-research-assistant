from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools import web_search, news_search, calculator
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

tools = [web_search, news_search, calculator]

system_prompt = (
    "You are a helpful research assistant with access to tools: news_search, web_search, and calculator. "
    "IMPORTANT RULES:\n"
    "1. Only call news_search or web_search when the user asks about a NEW topic or explicitly "
    "asks for updated/latest information.\n"
    "2. For follow-up questions that ask you to compare, summarize, analyze, or give an opinion "
    "about topics ALREADY discussed earlier in this conversation, do NOT call any tools — "
    "answer directly using the information already gathered.\n"
    "3. Use the calculator tool only for arithmetic.\n"
    "After gathering information, summarize the actual content found — "
    "include specific headlines, dates, and facts rather than just naming websites."
)

checkpointer = InMemorySaver()

agent = create_agent(llm, tools, system_prompt=system_prompt, checkpointer=checkpointer)