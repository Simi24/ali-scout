# ali-scout

Search AliExpress, read product reviews and tell whether a price is actually good — built to be driven by an LLM agent. It ships as a CLI with compact text or JSON output, an agent skill, and an optional MCP server.

```text
$ ali-scout search "sonoff snzb-02d" --limit 1
'sonoff snzb-02d' page 1 (169 results)
- [1005005372282766] 1-5PCS SONOFF SNZB-02D Zigbee Temperature Humidity Sensor ...
    9.83 EUR [GREAT] 30d low 13.00 (-24%) · ★4.9 · 3536 orders · ships from CN
    https://it.aliexpress.com/item/1005005372282766.html
```

## How it works

- **Search**: the AliExpress search page already embeds its results as JSON (`itemList`). One plain GET, no browser.
- **Reviews**: the public JSON endpoint `feedback.aliexpress.com/pc/searchEvaluation.do` returns machine-translated texts, a star breakdown and aggregated "impressions" (e.g. *accurate readings ×31*). It ignores sorting and star filters, so critical reviews are filtered client-side.
- **Price verdict without a database**: under the EU Omnibus directive (2019/2161) a store advertising a discount must show the **lowest price of the last 30 days**. AliExpress includes it in search results; ali-scout compares it with the current price (`great` / `fair` / `high` / `unknown`). On non-EU storefronts the low is usually missing.
- **Politeness**: a 1.5 s pause between requests and a 1-hour on-disk cache (`~/.cache/ali-scout`, or `ALI_SCOUT_CACHE`). AliExpress starts blocking after about a dozen searches in a row.

Not available: store names and per-variant prices — the product page goes through a signed API behind a captcha, and ali-scout does not try to get around it.

## Install

```bash
uv tool install git+https://github.com/Simi24/ali-scout
export ALI_SCOUT_LOCALE=it   # optional default
```

Or let your agent do it: [AGENTS.md](AGENTS.md) tells any coding agent how to install and set up the tool.

## Use it from an agent

The CLI works with any agent that has a shell. On top of it:

**Skill** — `skills/ali-scout/SKILL.md` follows the open [Agent Skills](https://agentskills.io) format, read by Claude Code, Codex, Gemini CLI, Cursor, GitHub Copilot and others. Copy or symlink `skills/ali-scout` into your agent's skills folder (e.g. `~/.claude/skills/`).

**Claude Code plugin** — the repo is also a plugin (skill + MCP server):

```text
/plugin marketplace add Simi24/shopping-scouts
/plugin install ali-scout@shopping-scouts
```

**MCP server** — for agents without a shell. It runs straight from GitHub with `uvx`, nothing to install:

```json
{
  "mcpServers": {
    "ali-scout": {
      "command": "uvx",
      "args": ["--from", "ali-scout[mcp] @ git+https://github.com/Simi24/ali-scout", "ali-scout-mcp"],
      "env": { "ALI_SCOUT_LOCALE": "it" }
    }
  }
}
```

This `mcpServers` block works in Claude Desktop, Cursor (`~/.cursor/mcp.json`) and Gemini CLI (`~/.gemini/settings.json`). In VS Code use the same server under `"servers"` in `.vscode/mcp.json`. In Codex (`~/.codex/config.toml`):

```toml
[mcp_servers.ali_scout]
command = "uvx"
args = ["--from", "ali-scout[mcp] @ git+https://github.com/Simi24/ali-scout", "ali-scout-mcp"]
env = { ALI_SCOUT_LOCALE = "it" }
```

The country comes from the environment the client passes to the server (`env` above, or your shell); without it the tool falls back to its default.

All the tools in the family: [shopping-scouts](https://github.com/Simi24/shopping-scouts).

## Usage

```bash
ali-scout search "sonoff snzb-02d" --sort orders --min-rating 4.5 --limit 5
ali-scout reviews 1005005372282766 --pages 4 --max-stars 3
ali-scout --locale de search "running gloves" --json
```

Storefronts: `it` (default), `de`, `us`. Set a default with `ALI_SCOUT_LOCALE`. Adding one is a line in `src/ali_scout/storefront.py`.

## Development

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format .
```

Tests run offline against saved fixtures in `tests/fixtures/`.

## Disclaimer

This project reads public AliExpress pages and endpoints for personal use. It is not affiliated with AliExpress, may break whenever the site changes, and AliExpress's terms of use may restrict automated access: use it responsibly and at your own risk.

## License

MIT
