"""ali-scout: search AliExpress, read reviews, judge the price.

  ali-scout [--locale it|de|us] search "<query>" [--sort best|orders|price_asc|price_desc|newest] [--page N]
                                [--limit N] [--min-rating 4.5] [--min-orders 100] [--json]
  ali-scout [--locale it|de|us] reviews <product_id> [--pages N] [--images] [--max-stars 3] [--json]

The price verdict compares the current price with the lowest price of the last 30 days, which EU stores
must show by law (Omnibus directive): great = at or below the low, fair = within +10%, high = above.
"""

import argparse
import sys

from ali_scout import http, render, storefront
from ali_scout.reviews import reviews
from ali_scout.search import Sort, filter_products, search

SORTS = {"best": Sort.BEST, "orders": Sort.ORDERS, "price_asc": Sort.PRICE_ASC, "price_desc": Sort.PRICE_DESC, "newest": Sort.NEWEST}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--locale", choices=storefront.LOCALES, help="storefront (default: $ALI_SCOUT_LOCALE or it)")
    p.add_argument("--no-cache", action="store_true", help="ignore the 1-hour cache")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="search products")
    s.add_argument("query")
    s.add_argument("--sort", choices=SORTS, default="best")
    s.add_argument("--page", type=int, default=1)
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--min-rating", type=float)
    s.add_argument("--min-orders", type=int)
    s.add_argument("--json", action="store_true")

    r = sub.add_parser("reviews", help="reviews of a product")
    r.add_argument("product_id")
    r.add_argument("--pages", type=int, default=1, help="pages of 100 reviews")
    r.add_argument("--images", action="store_true", help="only reviews with photos")
    r.add_argument("--max-stars", type=int, help="only reviews with at most N stars")
    r.add_argument("--json", action="store_true")
    return p.parse_args()


def run_search(args: argparse.Namespace) -> str:
    result = search(args.query, SORTS[args.sort], args.page, args.locale, use_cache=not args.no_cache)
    result = filter_products(result, args.limit, args.min_rating, args.min_orders)
    return result.model_dump_json(indent=1) if args.json else render.search(result)


def run_reviews(args: argparse.Namespace) -> str:
    result = reviews(args.product_id, args.pages, args.images, args.max_stars, args.locale, use_cache=not args.no_cache)
    return result.model_dump_json(indent=1) if args.json else render.reviews(result)


def main() -> None:
    args = parse_args()
    try:
        print(run_search(args) if args.cmd == "search" else run_reviews(args))
    except http.BlockedError as e:
        print(f"blocked by AliExpress: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
