from __future__ import annotations

import argparse
import json

from mcp.server.fastmcp import FastMCP

from catalog import fetch_document, search_documents

SERVER_INSTRUCTIONS = """
This is a demo MCP server for ChatGPT testing.
Use the search tool first to find relevant document ids.
Use the fetch tool after search when you need the full text of one document.
Search returns JSON shaped like {"results":[{"id":"...","title":"...","url":"..."}]}.
Fetch returns JSON shaped like {"id":"...","title":"...","text":"...","url":"...","metadata":{...}}.
""".strip()

READ_ONLY_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": False,
}

mcp = FastMCP("chatgpt-demo-mcp", instructions=SERVER_INSTRUCTIONS)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
def search(query: str, limit: int = 5) -> str:
    """Search the demo knowledge base for relevant documents."""
    results = search_documents(query, limit=limit)
    return json.dumps({"results": results}, indent=2)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
def fetch(id: str) -> str:
    """Fetch one document by the id returned from search."""
    try:
        document = fetch_document(id)
    except KeyError as exc:
        raise ValueError(str(exc)) from exc

    return json.dumps(document, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the demo MCP server with a transport that ChatGPT can use."
    )
    parser.add_argument(
        "--transport",
        default="streamable-http",
        choices=["streamable-http", "sse", "stdio"],
        help="Use streamable-http for ChatGPT testing.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind for HTTP transports.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind for HTTP transports.")
    args = parser.parse_args()

    if args.transport != "stdio":
        mcp.settings.host = args.host
        mcp.settings.port = args.port

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
