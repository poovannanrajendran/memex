#!/usr/bin/env python3
"""
memex_mcp.py — MCP server wrapping Memex runner_api.
"""

import os
import json
import requests
from mcp.server.fastmcp import FastMCP

# Configuration
RUNNER_BASE  = os.getenv("MEMEX_RUNNER_URL", "http://127.0.0.1:8000")
RUNNER_TOKEN = os.getenv("RUNNER_API_SECRET", "")

# Initialize FastMCP
server = FastMCP("memex")

@server.tool()
async def memex_search(query: str, type: str = None, limit: int = 8) -> str:
    """
    Search Poovi's Memex Second Brain — 7,483 pages covering Lloyd's/insurance,
    AI engineering, productivity, and podcast content.
    Returns matching sources, entities, concepts, or synthesis docs.
    """
    params = {"q": query, "limit": min(limit, 20)}
    if type:
        params["type"] = type
    
    r = requests.get(
        f"{RUNNER_BASE}/search",
        params=params,
        headers={"Authorization": f"Bearer {RUNNER_TOKEN}"},
        timeout=10
    )
    r.raise_for_status()
    return json.dumps(r.json(), indent=2)

@server.tool()
async def memex_get(type: str, slug: str) -> str:
    """
    Fetch the full content of a specific Memex wiki entry by type and slug.
    Use after memex_search to get full markdown content of a result.
    """
    r = requests.get(
        f"{RUNNER_BASE}/wiki/{type}/{slug}",
        headers={"Authorization": f"Bearer {RUNNER_TOKEN}"},
        timeout=10
    )
    r.raise_for_status()
    return json.dumps(r.json(), indent=2)

@server.tool()
async def memex_synthesis_list() -> str:
    """
    List all Memex deep-dive synthesis documents.
    """
    r = requests.get(
        f"{RUNNER_BASE}/wiki/synthesis/list",
        headers={"Authorization": f"Bearer {RUNNER_TOKEN}"},
        timeout=10
    )
    r.raise_for_status()
    return json.dumps(r.json(), indent=2)

@server.tool()
async def linkedin_post(content: str) -> str:
    """Post content directly to Poovi's LinkedIn profile via the runner API."""
    import requests as _requests
    r = _requests.post(
        f"{RUNNER_BASE}/linkedin/post",
        json={"content": content},
        headers={"Authorization": f"Bearer {RUNNER_TOKEN}"},
        timeout=20
    )
    if r.ok:
        return f"Posted to LinkedIn ({len(content)} chars)."
    return f"Failed: {r.status_code} {r.text}"

if __name__ == "__main__":
    server.run()
