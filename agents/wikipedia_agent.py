# -*- coding: utf-8 -*-
"""
Synergy Wikipedia Agent
Interfaces with the Wikipedia api, searching for specific factual information.
Optimized for short spoken paragraph responses.
"""

import wikipedia

class WikipediaAgent:
    def __init__(self):
        # Set Wikipedia language default to English
        wikipedia.set_lang("en")

    def search_summary(self, query: str) -> str:
        """Searches Wikipedia and extracts a 2-sentence summary outline for vocal synthesis."""
        if not query or not query.strip():
            return "What would you like me to look up on Wikipedia?"

        print(f"[*] Wikipedia querying for: '{query}'")
        try:
            # Query Wikipedia with 2 sentences limit for quick speech feedback
            summary = wikipedia.summary(query, sentences=2)
            return f"According to Wikipedia: {summary}"
            
        except wikipedia.DisambiguationError as d:
            options = d.options[:3]
            options_text = ", or ".join(options)
            return f"The term '{query}' is ambiguous. Did you mean: {options_text}?"
            
        except wikipedia.PageError:
            # Try a search as fallback
            suggested_results = wikipedia.search(query, results=3)
            if suggested_results:
                try:
                    alt_summary = wikipedia.summary(suggested_results[0], sentences=2)
                    return f"I couldn't find an exact page for '{query}', but looking up '{suggested_results[0]}': {alt_summary}"
                except Exception:
                    pass
            return f"I couldn't find any articles about '{query}' on Wikipedia."
            
        except Exception as e:
            return f"Wikipedia assistance failed with the following code error: {str(e)}"
