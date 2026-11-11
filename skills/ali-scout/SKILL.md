---
name: ali-scout
description: Search products on AliExpress, read their reviews and judge whether the price is good against the lowest price of the last 30 days. Use it when the user wants to buy something and weigh the options on AliExpress, compare cheap products, check whether a sale (11.11, Black Friday) discount is real, or find the recurring defects of a product ("search aliexpress for", "is it cheaper on ali?", "how much is X on aliexpress", "is this a good price?").
---

# ali-scout

## Setup (only if the command is missing)

- `ali-scout` not found: propose `uv tool install git+https://github.com/Simi24/ali-scout` and wait for the person to agree.
- Default storefront: set `ALI_SCOUT_LOCALE` (e.g. `it`) or pass the option on each call.

## Commands

```bash
# search: price, price verdict, rating, orders, ship-from country, tags
ali-scout search "<query>" [--sort best|orders|price_asc|price_desc|newest] [--limit 10] [--min-rating 4.5] [--min-orders 100] [--page N] [--json]

# reviews: star breakdown, aggregated impressions, texts (100 per page)
ali-scout reviews <product_id> [--pages N] [--max-stars 3] [--images] [--json]

# storefront: it (default), de, us — or set ALI_SCOUT_LOCALE
ali-scout --locale de search "<query>"
```

The default text output is compact and enough to reason on. Use `--json` only when you need to process the fields.

## Recommended flow

1. **One or two searches**, not ten: AliExpress blocks after about 12 requests in a row (exit code 2, "blocked"). If it happens, wait a few minutes. Repeated requests within an hour come from the cache.
   - Short queries, only the product words: `"running gloves touch"`, `"sonoff snzb-02d"`.
   - `--sort orders --min-rating 4.5` is the most reliable quality filter for generic products.
   - For an **exact model** (e.g. `"sonoff snzb-02d"`) keep the default sort: with `--sort orders` other best-selling products of the same brand float to the top.
   - Generic queries also return products from nearby categories (e.g. "running led light" returns bike lights): drop off-topic results and rephrase if needed.
2. **Pick 2-3 candidates** and read the critical reviews of each: `reviews <id> --pages 4 --max-stars 3`. Stars are not filtered server-side, so several pages are needed (4 pages = 400 reviews).
3. **Answer** with a comparison: price, verdict, rating and orders, recurring defects from the reviews, link.

## Reading the price verdict

EU stores must show the **lowest price of the last 30 days** when they advertise a discount (Omnibus directive). `price_check` compares it with the current price:

| verdict | meaning |
|---|---|
| `great` | at or below the 30-day low: the discount is real |
| `fair` | within +10% of the low |
| `high` | it sold for more than 10% less in the last month: better to wait |
| `unknown` | the low is not shown (no discount, new listing, or a non-EU storefront) |

- During big sales the 30-day low is usually the **pre-sale** price: `great` means "real discount", not "all-time low".
- `original_price` (the strikethrough price) is often inflated: do not use it alone to call a deal.
- Tags like **"first-time buyer price"** mean the price applies to new customers only. Tell the user.
- Tags like **"free shipping over 10€"**: below that threshold shipping is paid, so bundling items pays off.
- The price is the **cheapest variant** (size, color, number of pieces). Tell the user to check the variant in the app.
- Prices differ between storefronts for the same listing: when the user can buy from another EU storefront, compare with `--locale`.

## Limits

- Store name and per-variant prices are **not available**: the product page is behind a captcha. For branded products, tell the user to check in the app that the seller is the official store.
- Reviews are machine-translated into the storefront language; `variant` tells which variant the author bought and where it shipped from.
