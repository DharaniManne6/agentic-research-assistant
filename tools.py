from langchain_core.tools import tool
from ddgs import DDGS

@tool
def web_search(query: str) -> str:
    """Search the web for general information, facts, or how-to content on a topic."""
    results = DDGS().text(query, max_results=5)
    if not results:
        return "No results found."
    
    formatted = []
    for r in results:
        formatted.append(f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}")
    
    return "\n\n".join(formatted)

@tool
def news_search(query: str) -> str:
    """Search for recent news articles and headlines on a topic. 
    Use this for current events, stock news, company updates, or anything 'latest'."""
    results = DDGS().news(query, max_results=5)
    if not results:
        return "No news results found."
    
    formatted = []
    for r in results:
        formatted.append(f"Title: {r['title']}\nDate: {r.get('date', 'N/A')}\nSnippet: {r['body']}\nSource: {r.get('source', 'N/A')}\nURL: {r['url']}")
    
    return "\n\n".join(formatted)

@tool
def calculator(expression: str) -> str:
    """Evaluate a basic math expression. Use this for any arithmetic calculations.
    Input should be a valid Python math expression, e.g. '23 * 4 + 10'."""
    try:
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression."
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"