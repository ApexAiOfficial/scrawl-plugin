"""Both hosts' marketplaces and manifests agree, and credentials reach each host only the supported way."""

from __future__ import annotations

import re

from conftest import PLUGIN, ROOT, load_json, without_code_blocks

CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
CLAUDE_MCP = PLUGIN / ".mcp.json"
CODEX_MCP = PLUGIN / ".codex-mcp.json"


def test_both_marketplaces_are_apexai_scrawl_and_point_at_the_plugin() -> None:
    claude, codex = load_json(CLAUDE_MARKETPLACE), load_json(CODEX_MARKETPLACE)
    assert claude["name"] == codex["name"] == "apexai-scrawl"
    assert claude["owner"] == {"name": "ApexAiOfficial", "email": "support@apexaiofficial.com"}
    [claude_entry] = claude["plugins"]
    [codex_entry] = codex["plugins"]
    assert claude_entry["name"] == codex_entry["name"] == "scrawl"
    assert (ROOT / claude_entry["source"]).resolve() == PLUGIN.resolve()
    assert codex_entry["source"] == {"source": "local", "path": "./plugins/scrawl"}
    assert codex_entry["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
    assert codex_entry["category"]


def test_the_two_plugin_manifests_agree() -> None:
    claude, codex = load_json(CLAUDE_MANIFEST), load_json(CODEX_MANIFEST)
    for field in ("name", "version", "description", "author", "homepage", "repository", "license"):
        assert claude[field] == codex[field], field
    assert claude["name"] == "scrawl" and re.fullmatch(r"\d+\.\d+\.\d+", claude["version"])
    assert claude["license"] == "Apache-2.0"
    assert claude["author"] == {"name": "ApexAiOfficial", "email": "support@apexaiofficial.com",
                                "url": "https://github.com/ApexAiOfficial"}
    assert claude["homepage"] == "https://github.com/ApexAiOfficial/scrawl-plugin"
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## Unreleased: {claude['version']}" in changelog or f"## {claude['version']}" in changelog


def test_user_config_holds_the_key_as_a_required_secret_and_loopback_defaults() -> None:
    config = load_json(CLAUDE_MANIFEST)["userConfig"]
    assert set(config) == {"api_key", "mcp_url", "base_url"}
    key = config["api_key"]
    assert key["type"] == "string" and key["sensitive"] is True and key["required"] is True
    assert "default" not in key
    assert config["mcp_url"]["default"] == "http://127.0.0.1:8000/mcp"
    assert config["base_url"]["default"] == "http://127.0.0.1:8088"
    for option in config.values():
        assert option["title"] and option["description"]
        assert not option.get("sensitive") or option is key


def test_claude_mcp_takes_url_and_bearer_only_from_user_config() -> None:
    servers = load_json(CLAUDE_MCP)["mcpServers"]
    assert servers == {"scrawl": {"type": "http", "url": "${user_config.mcp_url}",
                                  "headers": {"Authorization": "Bearer ${user_config.api_key}"}}}
    text = CLAUDE_MCP.read_text(encoding="utf-8")
    # No environment variable, no default and no literal credential: only the declared settings.
    assert set(re.findall(r"\$\{([^}]*)\}", text)) == {"user_config.mcp_url", "user_config.api_key"}
    assert "bearer_token_env_var" not in text


def test_codex_mcp_uses_its_own_file_with_bearer_from_the_environment() -> None:
    manifest = load_json(CODEX_MANIFEST)
    assert manifest["mcpServers"] == "./.codex-mcp.json"   # without it Codex would read .mcp.json, unauthenticated
    assert manifest["skills"] == "./skills/"
    servers = load_json(CODEX_MCP)["mcpServers"]
    assert servers == {"scrawl": {"type": "http", "url": "http://127.0.0.1:8000/mcp",
                                  "bearer_token_env_var": "SCRAWL_API_KEY"}}
    assert servers["scrawl"]["url"] == load_json(CLAUDE_MANIFEST)["userConfig"]["mcp_url"]["default"]


def test_codex_interface_block() -> None:
    interface = load_json(CODEX_MANIFEST)["interface"]
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "category",
                  "capabilities", "websiteURL", "defaultPrompt", "composerIcon", "logo"):
        assert interface[field], field
    assert interface["displayName"] == "Scrawl" and interface["developerName"] == "ApexAiOfficial"
    for icon in (interface["composerIcon"], interface["logo"]):
        assert (PLUGIN / icon).is_file()


def test_nothing_the_hosts_would_refuse_or_run() -> None:
    """No hooks, no top-level bin/, no .app.json, no commands, no scripts: the plugin is skills and settings."""
    for path in ("hooks", "bin", ".app.json", "commands", "agents", "scripts", "agents/openai.yaml"):
        assert not (PLUGIN / path).exists(), path
    for manifest in (CLAUDE_MANIFEST, CODEX_MANIFEST):
        assert "hooks" not in load_json(manifest)
    allowed = {".md", ".json", ".svg", ""}
    for file in PLUGIN.rglob("*"):
        if file.is_file():
            assert file.suffix in allowed, file
            assert file.stat().st_size < 256 * 1024, file


def test_license_and_notice_ship_inside_the_plugin() -> None:
    for name in ("LICENSE", "NOTICE"):
        assert (PLUGIN / name).read_bytes() == (ROOT / name).read_bytes()
    assert "Apache License" in (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Copyright 2026 ApexAiOfficial" in (ROOT / "NOTICE").read_text(encoding="utf-8")


def test_readmes_are_long_enough_for_the_directory() -> None:
    """Anthropic's directory needs a README of at least 40 words in the plugin folder, outside code blocks."""
    for readme in (ROOT / "README.md", PLUGIN / "README.md"):
        words = re.findall(r"\w+", without_code_blocks(readme.read_text(encoding="utf-8")))
        assert len(words) >= 40, readme


def test_root_readme_documents_install_endpoints_privacy_and_support() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for needle in ("claude plugin marketplace add ApexAiOfficial/scrawl-plugin",
                   "claude plugin install scrawl@apexai-scrawl",
                   "codex plugin marketplace add ApexAiOfficial/scrawl-plugin",
                   "codex plugin add scrawl@apexai-scrawl",
                   "## Endpoints contacted", "## Privacy", "## Support", "support@apexaiofficial.com"):
        assert needle in readme, needle
