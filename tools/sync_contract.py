"""Vendor the MCP tool contract from a scrawl-sdk checkout and record where it came from.

    python tools/sync_contract.py PATH/TO/scrawl-sdk           # copy contracts/mcp_tools.json, rewrite MANIFEST.json
    python tools/sync_contract.py PATH/TO/scrawl-sdk --check   # exit 1 if the vendored copy differs

The plugin uses only ``mcp_tools.json``: tests check every MCP tool and argument a skill names against it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
NAME = "mcp_tools.json"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main(argv: list[str] | None = None) -> int:
    """Copy (or compare) the scrawl-sdk contract file; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sdk", type=Path, help="a scrawl-sdk checkout")
    parser.add_argument("--check", action="store_true", help="compare only; write nothing")
    args = parser.parse_args(argv)

    source_dir = args.sdk / "contracts"
    data = (source_dir / NAME).read_bytes()
    sdk_manifest = json.loads((source_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    expected = sdk_manifest["files"][NAME]["sha256"]
    if _digest(data) != expected:
        print(f"{source_dir / NAME} does not match its MANIFEST.json", file=sys.stderr)
        return 1
    if args.check:
        same = (CONTRACTS / NAME).read_bytes() == data
        print("up to date" if same else "the vendored contract differs from scrawl-sdk")
        return 0 if same else 1

    CONTRACTS.mkdir(exist_ok=True)
    (CONTRACTS / NAME).write_bytes(data)
    manifest = {
        "format": 1,
        "files": {NAME: {"bytes": len(data), "sha256": _digest(data)}},
        "source": {
            "repository": "https://github.com/ApexAiOfficial/scrawl-sdk",
            "path": f"contracts/{NAME}",
            "contract_digest": sdk_manifest["digest"],
            "backend_version": sdk_manifest["source"]["backend_version"],
            "synced": date.today().isoformat(),
        },
    }
    (CONTRACTS / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"vendored {NAME} ({len(data)} bytes) from contract {sdk_manifest['digest']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
