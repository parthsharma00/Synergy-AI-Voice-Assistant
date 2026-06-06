# -*- coding: utf-8 -*-
"""
Synergy Web Search Agent
Queries external search engines using duckduckgo-search, synthesizing live topics.
"""

from typing import Dict, List, Any

class WebSearchAgent:
    def __init__(self):
        pass

    def search_web(self, query: str) -> str:
        """Runs live query search on DuckDuckGo and summarizes the top text snippets."""
        if not query or not query.strip():
            return "What would you like me to search the web for?"

        print(f"[*] Search agent looking up: '{query}'")
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return "DuckDuckGo search module is not available in current environment."

        try:
            # We use the modern non-authenticated DDGS client contexts
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))

            if not results:
                return f"I ran a web search for '{query}' but could not find any relevant results."

            # Summarize the first key finding
            top_result = results[0]
            title = top_result.get("title", "")
            snippet = top_result.get("body", "")
            
            # If the snippet is excessively long, truncate for spoken clarity
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."

            return f"According to web search for '{query}': '{title}'. {snippet}"

        except Exception as e:
            return f"Web search failed. I recommend trying again. Full error details: {str(e)}"
