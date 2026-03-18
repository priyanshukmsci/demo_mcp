# Demo MCP Server For Claude Desktop

This repo contains a tiny Python MCP server you can expose to Claude Desktop for local end-to-end testing.

It exposes two read-only tools:

- `search(query, limit=5)` returns JSON with `results`, where each result includes `id`, `title`, and `url`
- `fetch(id)` returns the full document text and metadata for one result from `search`

## Files

- `claude_config.py` generates the Claude Desktop MCP config for this checkout
- `server.py` runs the MCP server
- `catalog.py` loads the demo knowledge base and handles search/fetch logic
- `demo_docs.json` contains the fake documents the server can query
- `tests/test_catalog.py` verifies the local search helpers

## Setup

Create a virtual environment and install the project:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -e .
```

Claude Desktop will launch the server for you over `stdio`, so you do not need to start `server.py` manually during normal use.

## Claude Desktop Configuration

On Windows, open Claude Desktop and go to:

1. `Settings`
2. `Developer`
3. `Edit Config`
4. In the file that Claude Desktop opens, keep that config file open for the next steps

Use Claude Desktop's `Edit Config` action to manually open the correct config file for your machine before you paste anything.

Generate the config JSON for this checkout with:

```powershell
py claude_config.py
```

Then paste or merge that output into the config file Claude Desktop opened for you.

If the config file is empty, you can paste the full output as-is.

If the config file already has an `"mcpServers"` object, add the generated `"demoMcp"` entry inside that object and keep the rest of the file unchanged.

If the config file already has other top-level settings but no `"mcpServers"` key yet, add the generated `"mcpServers"` object without removing the existing settings.

If you want to use a different interpreter, pass it explicitly:

```powershell
py claude_config.py `
  --python-path "C:\Path\To\python.exe"
```

Then fully quit and restart Claude Desktop. If the server starts correctly, you should see the MCP tools indicator in the chat box.

## Example Prompts

Once the server is connected, try:

- `Use the search tool to find Bluepine pricing, then fetch the pricing document and summarize the plans.`
- `Find the security policy and tell me about retention.`
- `What is on the Bluepine roadmap and which items are not committed?`

## Troubleshooting

If Claude Desktop does not show the MCP tools:

- Make sure the JSON is valid
- Make sure the paths are absolute paths
- Confirm that `.venv\Scripts\python.exe` exists
- Check logs in `%APPDATA%\Claude\logs`
- Look at `mcp.log` and `mcp-server-demoMcp.log`

If you use a different Python interpreter, replace the `command` path with that interpreter and keep the `server.py` path absolute.

## Optional Local Inspection

If you want to inspect the server outside Claude Desktop, run:

```powershell
py -m mcp dev server.py
```

## Test The Helper Logic

These tests do not require the MCP package:

```powershell
py -m unittest
```
