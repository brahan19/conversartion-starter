"""
Dynamic web search tool using Firecrawl API so agents can pass a query at runtime.
"""
import os
import logging
from typing import Type

import requests
from pydantic import BaseModel, Field

from crewai.tools import BaseTool

# Set up logging for Firecrawl debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        payload = {"query": query, "limit": 8}

        # Log the query being sent
        print("\n" + "="*80)
        print(f"🔍 FIRECRAWL SEARCH QUERY: {query}")
        print("="*80)

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Log raw response for debugging
            logger.info(f"Firecrawl API response status: {response.status_code}")
            logger.info(f"Firecrawl response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
            
            if not data.get("success") or "data" not in data:
                print(f"⚠️  FIRECRAWL ERROR RESPONSE: {data}")
                return str(data)
            
            results = data.get("data", [])
            if not results:
                print("⚠️  FIRECRAWL: No search results found.")
                return "No search results found."
            
            # Log number of results
            print(f"✅ FIRECRAWL FOUND {len(results)} RESULTS:")
            print("-"*80)
            
            parts = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "No title")
                url_link = r.get("url", "")
                desc = r.get("description", "") or r.get("markdown", "")[:300]
                
                # Print each result for visibility
                print(f"\n[{i}] {title}")
                print(f"    🔗 {url_link}")
                print(f"    📄 {desc[:200]}...")
                
                parts.append(f"{i}. {title}\n   URL: {url_link}\n   {desc}")
            
            print("="*80 + "\n")
            
            return "\n\n".join(parts)
        except requests.exceptions.RequestException as e:
            error_msg = f"Firecrawl API error: {e}"
            print(f"❌ {error_msg}")
            logger.error(f"Firecrawl request error: {e}", exc_info=True)
            return error_msg
        except Exception as e:
            error_msg = f"Error during search: {e}"
            print(f"❌ {error_msg}")
            logger.error(f"Firecrawl unexpected error: {e}", exc_info=True)
            return error_msg
