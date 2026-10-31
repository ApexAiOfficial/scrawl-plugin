# Scrawl in Claude Code

## Install

```bash
claude plugin marketplace add ApexAiOfficial/scrawl-plugin      # add #<tag> to pin a release
claude plugin install scrawl@apexai-scrawl
```

Inside a session: `/plugin marketplace add ApexAiOfficial/scrawl-plugin`, then
`/plugin install scrawl@apexai-scrawl`. Without SSH keys for GitHub, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`
first. For a team, `--scope project` on both commands records the marketplace and the plugin in the project's
`.claude/settings.json`, so everyone who trusts the project is offered them; each person still sets their own
key.

## Configure

```bash
claude plugin install scrawl@apexai-scrawl --config mcp_url=https://scrawl.example/mcp
```

or, in a session, `/plugin configure scrawl@apexai-scrawl`, which also asks for the key in a masked field.

| Option | Type | Default | Stored in |
| --- | --- | --- | --- |
| `api_key` | string, **sensitive, required** | none | The platform's secure credential store; on Linux, Claude Code 2.1.282 keeps it in `.credentials.json` (mode 600) in its configuration directory. Never in `settings.json` |
| `mcp_url` | string | `http://127.0.0.1:8000/mcp` | `pluginConfigs` in your `settings.json` |
| `base_url` | string | `http://127.0.0.1:8088` | `pluginConfigs` in your `settings.json` |

Enter the key through the masked dialog rather than `--config api_key=…`, which would leave it in your shell
history.

How the settings are used:

- `.mcp.json` declares one MCP server, `scrawl`, of type `http`. Its URL is `${user_config.mcp_url}` and its
  only header is `Authorization: Bearer ${user_config.api_key}`. Nothing in it reads an environment variable.
- The MCP server is registered only after the required key is set; until then `claude mcp list` does not show
  it, so nothing connects anywhere.
- `base_url` is substituted into the skills (it is not secret), so they can tell you which value to export
  as `SCRAWL_BASE_URL` for the `scrawl` CLI. The CLI never sees the plugin's key: it reads `SCRAWL_API_KEY`
  from your shell.
- Use `https://` for any MCP URL that is not on this machine. Claude Code 2.1.282 accepts a plain `http://`
  URL to another host here without a warning and sends the key over it unencrypted: `claude plugin validate`
  checks only URLs written into `.mcp.json`, never the value you configure. The setup skill checks the
  configured URL and warns.
- If you use only the `scrawl` CLI, leave `api_key` unset: the MCP server then stays off and nothing is sent
  to the default URL.

## Check it

```bash
claude plugin list --json                    # the plugin, with its resolved mcpServers block
claude mcp get plugin:scrawl:scrawl          # URL, type, header (redacted) and connection status
claude plugin details scrawl@apexai-scrawl   # skills, MCP server, projected context cost
```

In a session, `/mcp` shows the server and its tools (`mcp__plugin_scrawl_scrawl__apex_scrapy_*`), and the
setup skill (`/scrawl:setup`) walks through the rest.

## Skills

`/scrawl:scrawl` (overview), `/scrawl:setup`, `/scrawl:scrape`, `/scrawl:map`, `/scrawl:crawl`,
`/scrawl:extract`, `/scrawl:ask`, `/scrawl:datasets` and `/scrawl:downloads`. Claude also picks them up
by itself when a request matches. The earlier `/scrawl:scrape` and `/scrawl:map` commands are now skills of
the same names.

## Update and remove

```bash
claude plugin marketplace update apexai-scrawl
claude plugin update scrawl@apexai-scrawl
claude plugin uninstall scrawl@apexai-scrawl
```

Auto-update is off by default for third-party marketplaces.

## Other Claude surfaces

What Anthropic's platform-support documentation says about other surfaces (not tested here):

| Surface | What loads |
| --- | --- |
| Claude Code (terminal, IDE, desktop Code tab) | Skills and the MCP server |
| claude.ai chat, Claude desktop chat | Skills only: chat ignores an MCP server whose URL comes from a plugin setting |
| Cowork | Skills only: Cowork ignores an MCP server that needs a setting without a default (the key) |

A Claude connector for claude.ai needs a public HTTPS endpoint with OAuth sign-in, which Scrawl does not offer
yet (see [chatgpt.md](chatgpt.md); the same server work enables both).

## Submitting to Anthropic's plugin directory

The plugin folder (`plugins/scrawl/`) is laid out for the directory's checks: a README of more than 40 words
and a `LICENSE` in the folder, `license` in `plugin.json`, the credential only through a `sensitive`
`userConfig` option, a remote MCP `url` that is a `${user_config.…}` reference, no hooks, no top-level `bin/`,
and text and SVG files only. Two things a reviewer may look at:

- `plugins/scrawl/.codex-mcp.json` names `SCRAWL_API_KEY` for Codex. Claude Code never reads that file, but
  the scan may hold the version for a person to confirm that.
- The skills tell the agent to use the `scrawl` CLI, which reads `SCRAWL_API_KEY` from the user's shell.

Submit the `plugins/scrawl` folder on its own from claude.ai/directory/manage (a paid plan is required).
