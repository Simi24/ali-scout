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
```

## Usage

```bash
ali-scout search "sonoff snzb-02d" --sort orders --min-rating 4.5 --limit 5
ali-scout reviews 1005005372282766 --pages 4 --max-stars 3
ali-scout --locale de search "running gloves" --json
```

Storefronts: `it` (default), `de`, `us`. Set a default with `ALI_SCOUT_LOCALE`. Adding one is a line in `src/ali_scout/storefront.py`.

## Agent skill

`skills/ali-scout/SKILL.md` tells an agent when to use the tool, how to keep within the rate limit and how to read the price verdict. For Claude Code:

```bash
git clone https://github.com/Simi24/ali-scout
ln -s "$PWD/ali-scout/skills/ali-scout" ~/.claude/skills/ali-scout
```

## MCP server (optional)

```bash
uv tool install "ali-scout[mcp] @ git+https://github.com/Simi24/ali-scout"
```

```json
{
  "mcpServers": {
    "ali-scout": { "command": "ali-scout-mcp" }
  }
}
```

Tools: `search_products`, `product_reviews`.

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
