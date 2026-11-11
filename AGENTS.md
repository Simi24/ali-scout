# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Gemini CLI, Cursor, Copilot...) working with this repository.

## What this is
`ali-scout`: search AliExpress, read reviews and judge prices against the 30-day low, for LLM agents. A Python CLI with compact text or JSON output, an agent skill in
`skills/ali-scout/SKILL.md` (Agent Skills format), and an optional MCP server.

## Setting it up for a user
1. **Install the CLI** (needs [uv](https://docs.astral.sh/uv/)): `uv tool install git+https://github.com/Simi24/ali-scout`. Ask before installing.
2. **Install the skill** in the agent's skills folder, e.g. `~/.claude/skills/ali-scout` for Claude Code: copy or symlink
   `skills/ali-scout`. Agents without skills support can read `skills/ali-scout/SKILL.md` directly.
3. No API key needed.
4. **Check**: `ali-scout search "usb c cable" --limit 1`.

Agents without a shell can use the MCP server instead: see "MCP server" in README.md for client configurations.

## Developing
```bash
uv sync
uv run pytest            # offline, against tests/fixtures/
uv run ruff check . && uv run ruff format .
```
Keep code, comments and docs in English. Never commit API keys or personal data in fixtures.
