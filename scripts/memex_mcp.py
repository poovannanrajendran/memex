#!/usr/bin/env python3
"""
memex_mcp.py — stdio MCP server wrapping Memex runner_api.

OpenClaw registers this as a stdio MCP server via SSH. It exposes three tools:
  - memex_search        : full-text search across wiki_index
  - memex_get           : fetch a specific wiki entry by type + slug
  - memex_synthesis_list: list all synthesis documents

OpenClaw config (on ai-node-01 ~/.openclaw/config.json5):
  mcp.servers.memex = {
    command: "ssh",
    args: ["-i", "/home/openclaw/.ssh/id_ed25519", "-o", "StrictHostKeyChecking=no",
           "labadmin@192.168.1.30",
           "MEMEX_RUNNER_URL=http://127.0.0.1:8000 RUNNER_API_SECRET=<token>
            python3 /home/labadmin/memex/scripts/memex_mcp.py"]
  }

Security: restrict SSH key to this command only in authorized_keys:
  command="python3 /home/labadmin/memex/scripts/memex_mcp.py",no-port-forwarding ssh-ed25519 ...
"""

import sys
import json
import os
import requests

RUNNER_URL = os.getenv("MEMEX_RUNNER_URL", "http://127.0.0.1:8000")
TOKEN      = os.getenv("RUNNER_API_SECRET", "")
HEADERS    = {"Authorization": f"Bearer {TOKEN}"}
TIMEOUT    = 10

TOOLS = [
    {
        "name": "memex_search",
        "description": (
            "Search Poovi's Memex Second Brain — 7,483 pages covering Lloyd's/insurance, "
            "AI engineering, productivity, and podcast content. "
            "Returns matching sources, entities, concepts, or synthesis docs. "
            "Use this to ground answers in Poovi's existing knowledge."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search terms — keywords, concept names, entity names"
                },
                "type": {
                    "type": "string",
                    "enum": ["sources", "entities", "concepts", "synthesis"],
                    "description": "Filter by content type. Omit to search all types."
                },
                "limit": {
                    "type": "integer",
                    "default": 8,
                    "description": "Max results to return (1-20)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "memex_get",
        "description": (
            "Fetch the full content of a specific Memex wiki entry by type and slug. "
            "Use after memex_search to get full markdown content of a result."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["sources", "entities", "concepts", "synthesis"],
                    "description": "Content type"
                },
                "slug": {
                    "type": "string",
                    "description": "Page slug (snake_case filename without .md)"
                }
            },
            "required": ["type", "slug"]
        }
    },
    {
        "name": "memex_synthesis_list",
        "description": (
            "List all Memex deep-dive synthesis documents. "
            "These are the highest-value pages — cross-source analyses on key topics "
            "like Lloyd's + AI, agent frameworks, and multi-agent memory. "
            "Call this first to discover which synthesis docs exist before fetching full content."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def call_runner(method: str, path: str, params: dict = None) -> dict:
    try:
        r = requests.request(
            method,
            f"{RUNNER_URL}{path}",
            params=params,
            headers=HEADERS,
            timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


def handle(req: dict) -> dict:
    method = req.get("method", "")
    rid    = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "memex", "version": "1.0.0"}
            }
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}

    if method == "tools/call":
        name = req.get("params", {}).get("name", "")
        args = req.get("params", {}).get("arguments", {})

        if name == "memex_search":
            params = {"q": args.get("query", ""), "limit": min(args.get("limit", 8), 20)}
            if args.get("type"):
                params["type"] = args["type"]
            result = call_runner("GET", "/search", params=params)

        elif name == "memex_get":
            result = call_runner("GET", f"/wiki/{args.get('type')}/{args.get('slug')}")

        elif name == "memex_synthesis_list":
            result = call_runner("GET", "/wiki/synthesis/list")

        else:
            result = {"error": f"Unknown tool: {name}"}

        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }
        }

    # notifications — no response needed
    if method.startswith("notifications/"):
        return None

    return {
        "jsonrpc": "2.0",
        "id": rid,
        "error": {"code": -32601, "message": f"Method not found: {method}"}
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
