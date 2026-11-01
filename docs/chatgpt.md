# ChatGPT: status and the path to support

**ChatGPT cannot use Scrawl yet.** This page says why, exactly what remains, and what would change in this
repository. The plugin installs and authenticates in the Codex CLI today; see [codex.md](codex.md).

## Why not today

| ChatGPT requires | Scrawl 0.8.0 has |
| --- | --- |
| A public HTTPS MCP endpoint (a Secure MCP Tunnel serves private testing only, never a published plugin) | An MCP endpoint bound to loopback only |
| No auth, or OAuth 2.1 sign-in. ChatGPT cannot send a custom API key | A per-request ApexAPI key as a bearer token |
| Protected resource metadata (RFC 9728) whose `authorization_servers` names an OAuth server | Protected resource metadata with no authorization server |

An API key typed into ChatGPT is not an option: OpenAI's plugin authentication supports `noauth` and `oauth2`
only, and the submission portal's connection form does not accept API-key declarations.

## What remains, on the server

1. **A public endpoint.** Serve `/mcp` over HTTPS on a public host, with the same per-request auth, rate
   limits and policy gates as today, and the abuse controls a public endpoint needs.
2. **An OAuth 2.1 authorization server** in front of ApexAPI accounts (an external identity provider, or one
   built into ApexAPI):
   - authorization-code flow with PKCE `S256` (`code_challenge_methods_supported` includes `S256`);
   - authorization server metadata (RFC 8414) and the resource metadata's `authorization_servers` pointing at
     it;
   - client registration by Client ID Metadata Document (preferred; ChatGPT's client ID is an HTTPS URL) and,
     for older clients, Dynamic Client Registration;
   - the redirect URI `https://chatgpt.com/connector_platform_oauth_redirect` allowed;
   - the `resource` parameter copied into the token's audience, and checked on every request, so a token
     minted for another service is refused;
   - `iss` returned in authorization responses (RFC 9207) if the metadata advertises it;
   - token scopes mapped to the existing ApexAPI scopes, so a signed-in user sees the same tools a key with
     those scopes would.
3. **Per-tool security schemes** (`securitySchemes` with `oauth2`) on every tool, and server-side token,
   scope and audience checks on every call.
4. **Tool metadata for review:** every tool keeps `title`, `readOnlyHint`, `destructiveHint` and
   `openWorldHint` (scraping tools reach the open web, so `openWorldHint: true`), with read and write
   actions in separate tools.

The same OAuth endpoint also unlocks a Claude connector for claude.ai and the Claude apps: Anthropic's
connector directory lists servers with OAuth (DCR or CIMD) or no auth, and treats a static bearer token as a
private deployment only.

## What would change in this repository

- `plugins/scrawl/.codex-plugin/plugin.json`: point `mcpServers` at an MCP entry for the public URL that
  uses OAuth instead of `bearer_token_env_var`, and add `privacyPolicyURL` and `termsOfServiceURL` (HTTPS
  pages that do not exist yet) to `interface`.
- `.agents/plugins/marketplace.json`: keep `policy.authentication` `ON_INSTALL` so users sign in when they
  install.
- `.app.json`: added only once OpenAI issues an app ID for the listing; it is left out until then.
- Claude Code's `.mcp.json`: the `mcp_url` default becomes the public URL; the bearer header and the
  `api_key` setting can stay for API-key access, or give way to Claude Code's own OAuth sign-in.
- Logos: the submission wants raster `logo` and `composerIcon` assets; the current icon is an SVG.
- Nothing changes in the skills: they already avoid hooks, commands and host-specific arguments, which the
  portal would strip or reject.

## Submitting to OpenAI (after the server work)

- An organization owner or a member with app-management rights, with identity verification.
- Domain verification: serve the challenge token at `/.well-known/openai-apps-challenge` on the MCP host.
- Listing assets: logo and composer icon, and HTTPS website, support, privacy and terms URLs.
- Review materials: a reviewer test account without MFA, five positive and three negative test prompts, and
  a demo video.
- One listing reaches both ChatGPT and Codex. Packages with hooks are refused (this one has none).

## A future app with UI

An MCP app adds interactive widgets to the same server; it is optional and builds on the work above. Widgets
that would help Scrawl users: an asset picker (choose which found files to download), a confirmation dialog
for a billable asset job showing the quote, a crawl progress view, a dataset diff view, and a field table for
dataset queries. What it would take:

- Each widget is a `ui://` resource served with the MIME type `text/html;profile=mcp-app` and bound to one tool
  through `_meta.ui.resourceUri`; the tool still returns plain JSON, so hosts without widgets keep working.
- The widget runtime (`@modelcontextprotocol/ext-apps`) is inlined into the HTML: the iframe's content policy
  blocks loading it from a CDN.
- **Scraped content stays untrusted inside the widget:** render every page-derived string as text, never as
  HTML; open links only through the host (`openLink`); inline images as data URLs.
- Results stay under the host's tool-result cap (about 150,000 characters in claude.ai and Claude Desktop,
  per Anthropic's MCP app guidance; ChatGPT's own limit needs checking before relying on a size): page large
  results and fetch heavy data through helper tools hidden from the model (`_meta.ui.visibility: ["app"]`).
- Anthropic's connector directory sets widget rules (at most 500 px inline height, no nested scrolling, 44 pt
  touch targets, light and dark themes from the host, 3 to 5 screenshots); OpenAI's app review has its own
  requirements, to be checked at submission.
- Simple confirmations (a yes/no on a quote) can use MCP elicitation instead of a widget, with a fallback for
  hosts that do not support it.

## What works with OpenAI tools today

- **Codex** with this plugin: bearer key from `SCRAWL_API_KEY` ([codex.md](codex.md)).
- **The OpenAI Agents SDK** can connect to a Streamable HTTP MCP server with an `Authorization` header, which
  fits Scrawl's per-request key, given a Scrawl MCP endpoint it can reach. This repository does not test it.
