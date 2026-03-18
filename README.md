# ChatGPT Demo MCP Server

This repo contains a tiny Python MCP server you can expose to ChatGPT for end-to-end testing.

It exposes two read-only tools:

- `search(query, limit=5)` returns JSON with `results`, where each result includes `id`, `title`, and `url`
- `fetch(id)` returns the full document text and metadata for one result from `search`

The tool shapes follow the `search` and `fetch` pattern OpenAI documents for remote MCP servers used by ChatGPT and deep research workflows.

## Files

- `server.py` runs the MCP server
- `catalog.py` loads the demo knowledge base and handles search/fetch logic
- `demo_docs.json` contains the fake documents ChatGPT can query
- `tests/test_catalog.py` verifies the local search helpers

## Setup

Create a virtual environment and install the project:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -e .
```

You can also install the dependency directly if you do not want editable mode:

```powershell
py -m pip install "mcp[cli]"
```

## Run The Server

For ChatGPT, use Streamable HTTP:

```powershell
py server.py --transport streamable-http --port 8000
```

The default MCP endpoint should be:

```text
http://127.0.0.1:8000/mcp
```

You can also try the inspector locally:

```powershell
py -m mcp dev server.py
```

## Test In Copilot

The easiest way to test this MCP server in GitHub Copilot is in VS Code, because you can run it locally over `stdio` and avoid tunnels completely.

This repo now includes a ready-to-use workspace config at `.vscode/mcp.json`.

In VS Code:

1. Open this folder.
2. Open the Chat view and switch to `Agent` mode.
3. Run `MCP: List Servers` from the Command Palette if the server does not appear automatically.
4. Start the `demoMcp` server.
5. In the tools picker, make sure the MCP tools are enabled for the chat.
6. Try a prompt like `Use #search to find Bluepine pricing, then use #fetch and summarize the plans.`

If `py` does not resolve inside VS Code on your machine, change the `command` in `.vscode/mcp.json` to your Python path, for example:

```json
{
  "servers": {
    "demoMcp": {
      "type": "stdio",
      "command": ".venv\\Scripts\\python.exe",
      "cwd": "${workspaceFolder}",
      "args": ["server.py", "--transport", "stdio"]
    }
  }
}
```

If you still do not see MCP options in Copilot, your organization may have disabled MCP access in VS Code policy.

## Test In Claude Desktop

Claude Desktop can run this MCP server locally over `stdio`, so you do not need any tunnel.

On Windows, open Claude Desktop, then go to:

1. `Settings`
2. `Developer`
3. `Edit Config`

Claude Desktop stores the config at:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration:

```json
{
  "mcpServers": {
    "demoMcp": {
      "command": "py",
      "args": [
        "C:\\Users\\kumapri2\\dev\\MCP_test\\server.py",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

Then fully quit and restart Claude Desktop. If the server starts correctly, you should see the MCP tools indicator in the chat box.

Try a prompt like:

- `Use the search tool to find Bluepine pricing, then fetch the pricing document and summarize the plans.`

If Claude Desktop does not show the MCP tools:

- Make sure the JSON is valid
- Make sure the paths are absolute paths, not relative ones
- Check logs in `%APPDATA%\Claude\logs`
- Look at `mcp.log` and `mcp-server-demoMcp.log`

If `py` does not work inside Claude Desktop on your machine, replace `command` with your full Python path and keep the `server.py` path absolute.

## Expose It To ChatGPT

ChatGPT needs a public URL for a remote MCP server. If `localtunnel` hangs, use a Cloudflare Quick Tunnel instead.

You do not need admin access for this. Download the standalone Windows executable into this repo or your Downloads folder:

```powershell
New-Item -ItemType Directory -Force .\tools | Out-Null
Invoke-WebRequest `
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe `
  -OutFile .\tools\cloudflared.exe
```

Then start the tunnel:

```powershell
.\tools\cloudflared.exe tunnel --url http://localhost:8000
```

If `cloudflared` hangs with a QUIC timeout such as `failed to dial to edge with quic: timeout: no recent network activity`, force HTTP/2 instead:

```powershell
.\tools\cloudflared.exe tunnel --protocol http2 --url http://localhost:8000
```

Use the public HTTPS URL from your tunnel and append `/mcp`, for example:

```text
https://random-name.trycloudflare.com/mcp
```

Then connect that URL in ChatGPT developer mode.

Keep the MCP server on `streamable-http`. Cloudflare Quick Tunnels do not support SSE.

If HTTP/2 also times out, your network is likely blocking outbound traffic to Cloudflare Tunnel on port `7844`. In that case, try a different network such as a mobile hotspot.

## Example Prompts

Once the server is connected, try:

- `Search Bluepine pricing and summarize the plans.`
- `Find the security policy and tell me about retention.`
- `What is on the Bluepine roadmap and which items are not committed?`

## Test The Helper Logic

These tests do not require the MCP package:

```powershell
py -m unittest
```
