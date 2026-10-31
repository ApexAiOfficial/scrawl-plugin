# Using the plugin with a self-hosted Scrawl server

The plugin's defaults assume a Scrawl server on the same machine as the agent:

| | Default | What answers there |
| --- | --- | --- |
| MCP URL | `http://127.0.0.1:8000/mcp` | The server's MCP endpoint over Streamable HTTP |
| API base URL | `http://127.0.0.1:8088` | ApexAPI, which the `scrawl` CLI uses |

Change them in Claude Code with `/plugin configure scrawl@apexai-scrawl`, or in Codex as described in
[codex.md](codex.md). The host sends your key to whatever listens at the MCP URL, so if another program on the
machine may hold port 8000, run Scrawl's MCP server on another port and set the URL to match.

## What the MCP endpoint expects

Scrawl 0.8.0 serves MCP over HTTP like this:

- **One route, `POST /mcp`**, stateless, answering with JSON. Other methods get 405, so a client's optional
  `GET` listen stream is simply declined.
- **Every request carries its own key** as `Authorization: Bearer <ApexAPI key>`. No key: 401 with a
  `WWW-Authenticate` challenge that points to the protected resource metadata at
  `/.well-known/oauth-protected-resource/mcp`. A refused key: 401 `invalid_token`. The metadata names no
  authorization server, because keys are issued by the server's operator, not through a browser sign-in.
- **Scopes decide which tools a key sees.** `tools/list` returns only the tools the key's scopes allow
  (`scrape:write`, `jobs:read`, `artifacts:read`, `credits:read`, `ai:use`), and every call is checked again.
- **A per-account request allowance** per minute (set by the operator) answers 429 with `Retry-After`.
- **Loopback only.** The server binds the MCP endpoint to `127.0.0.1`, `localhost` or `::1` and refuses
  anything else, so the agent must run on the server's machine to use the MCP route. Agents on other machines
  use the CLI route against the server's HTTPS API.

The operator starts the MCP server in its Streamable HTTP mode on a loopback address (port 8000 unless
configured otherwise), issues API keys with the scopes each user needs, and decides whether optional features
such as browser rendering and asset extraction are enabled. The operator can also limit the MCP server to its
read-only tools.

## Check the connection

```bash
claude mcp get plugin:scrawl:scrawl     # Claude Code: URL, header (redacted), status
codex mcp list --json                   # Codex: URL and "auth_status": "bearer_token"
scrawl doctor                           # the CLI route: base URL, TLS, reachability, key
```

A refused connection means nothing listens at the URL. A 401 means the key is missing or not accepted.

## The CLI against a remote server

The `scrawl` CLI talks to ApexAPI and works from any machine that can reach it:

```bash
export SCRAWL_BASE_URL=https://scrawl.example
export SCRAWL_API_KEY=...
scrawl doctor
```

It sends the key only over `https://`, or plain `http://` to this machine. `SCRAWL_ALLOW_INSECURE_HTTP=1`
lifts that for a trusted private network; avoid it otherwise.
