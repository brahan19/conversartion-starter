"""
Dynamic web search tool using Firecrawl API so agents can pass a query at runtime.
"""
import os
from typing import Type

import requests
from pydantic import BaseModel, Field

from crewai.tools import BaseTool


class FirecrawlSearchInput(BaseModel):
    """Input schema for dynamic Firecrawl search."""

    query: str = Field(..., description="Search query for web, blog, or video search")


class FirecrawlSearchTool(BaseTool):
    """Tool to search the web via Firecrawl API. Use for general web, blog, and video search. Pass the search query when calling."""

    name: str = "Firecrawl Web Search"
    description: str = (
        "Searches the web using Firecrawl. Use this for general web search, blog posts, or video content. "
        "Provide a clear search query string."
    )
    args_schema: Type[BaseModel] = FirecrawlSearchInput

    def _run(self, query: str) -> str:
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            return "Error: FIRECRAWL_API_KEY is not set in the environment."

        url = "https://api.firecrawl.dev/v1/search"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {"query": query, "limit": 5}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            if not data.get("success") or "data" not in data:
                return str(data)
            results = data.get("data", [])
            if not results:
                return "No search results found."
            parts = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "No title")
                url_link = r.get("url", "")
                desc = r.get("description", "") or r.get("markdown", "")[:300]
                parts.append(f"{i}. {title}\n   URL: {url_link}\n   {desc}")
            return "\n\n".join(parts)
        except requests.exceptions.RequestException as e:
            return f"Firecrawl API error: {e}"
        except Exception as e:
            return f"Error during search: {e}"
