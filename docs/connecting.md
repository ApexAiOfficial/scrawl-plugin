# Connecting the plugin to Scrawl

Scrawl is a service that ApexAi operates. The plugin reaches it by two routes: Scrawl's MCP endpoint, and
ApexAPI through the `scrawl` CLI. Both need the endpoint and the API key ApexAi provides for your account.
Scrawl's public hosted access is not open yet: there is no public endpoint or sign-up.

## The plugin's defaults

| | Default | Why |
| --- | --- | --- |
| MCP URL | `http://127.0.0.1:8000/mcp` | A loopback address: Scrawl's MCP server currently accepts only local connections. There is no hosted Scrawl MCP endpoint |
| API base URL | `http://127.0.0.1:8088` | A loopback address, the same default as the `scrawl` CLI, which has no built-in remote default |

Set them to the endpoints ApexAi provides for your account: in Claude Code with
`/plugin configure scrawl@apexai-scrawl`, in Codex as described in [codex.md](codex.md), and for the CLI with
`SCRAWL_BASE_URL`. The host sends your key to whatever listens at the MCP URL. When no Scrawl MCP endpoint
answers there, leave the key unset in Claude Code, or switch the entry off in Codex
([codex.md](codex.md#switch-the-mcp-server-off)), and use the CLI route.

## What Scrawl's MCP endpoint expects

Scrawl 0.8.0 serves MCP over HTTP like this:

- **One route, `POST /mcp`**, stateless, answering with JSON. Other methods get 405, so a client's optional
  `GET` listen stream is simply declined.
- **Every request carries its own key** as `Authorization: Bearer <ApexAPI key>`. No key: 401 with a
  `WWW-Authenticate` challenge that points to the protected resource metadata at
  `/.well-known/oauth-protected-resource/mcp`. A refused key: 401 `invalid_token`. The metadata names no
  authorization server, because ApexAi issues the keys; there is no browser sign-in.
- **Scopes decide which tools a key sees.** `tools/list` returns only the tools the key's scopes allow
  (`scrape:write`, `jobs:read`, `artifacts:read`, `credits:read`, `ai:use`), and every call is checked again.
- **A per-account request allowance** per minute answers 429 with `Retry-After`.
- **Loopback only.** Scrawl's MCP server accepts connections only on `127.0.0.1`, `localhost` or `::1` and
  refuses anything else, so it cannot be reached over a network. The CLI route, over Scrawl's HTTPS ApexAPI
  endpoint, works from any machine that can reach that endpoint.

ApexAi issues each key with the scopes its account needs and decides which optional features, such as asset
extraction and AI features, are enabled; an MCP endpoint can also be limited to its read-only tools. Scrawl
does not offer browser rendering today; the skills treat a `browser_unavailable` error as "not available here"
and use a plain scrape instead.

## Check the connection

```bash
claude mcp get plugin:scrawl:scrawl     # Claude Code: URL, header (redacted), status
codex mcp list --json                   # Codex: URL and "auth_status": "bearer_token"
scrawl doctor                           # the CLI route: base URL, TLS, reachability, key
```

A refused connection means nothing listens at the URL. A 401 means the key is missing or not accepted.

## The CLI route

The `scrawl` CLI talks to ApexAPI and works from any machine that can reach the endpoint ApexAi provides for
your account:

```bash
export SCRAWL_BASE_URL=https://scrawl.example   # the ApexAPI endpoint ApexAi provides for your account
export SCRAWL_API_KEY=...
scrawl doctor
```

It sends the key only over `https://`, or plain `http://` to this machine. `SCRAWL_ALLOW_INSECURE_HTTP=1`
lifts that for a trusted private network; avoid it otherwise.
