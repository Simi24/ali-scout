"""MCP server (stdio) on top of the same functions as the CLI. Needs the extra: uv sync --extra mcp."""

from fastmcp import FastMCP

from ali_scout.models import ReviewPage, SearchResult
from ali_scout.reviews import reviews
from ali_scout.search import Sort, filter_products, search

mcp = FastMCP("ali-scout")


@mcp.tool
def search_products(
    query: str,
    sort: Sort = Sort.BEST,
    page: int = 1,
    limit: int = 10,
    min_rating: float | None = None,
    min_orders: int | None = None,
    locale: str | None = None,
) -> SearchResult:
    """Search AliExpress. Each product has price_check: the current price against the lowest price of the last
    30 days that EU stores must show by law (great = at or below the low, fair = within +10%, high = above,
    unknown = low not shown). locale: it (default), de, us. Keep queries short."""
    return filter_products(search(query, sort, page, locale), limit, min_rating, min_orders)


@mcp.tool
def product_reviews(
    product_id: str, pages: int = 1, with_images: bool = False, max_stars: int | None = None, locale: str | None = None
) -> ReviewPage:
    """Reviews of a product, translated into the storefront language: star breakdown, aggregated impressions and
    texts, 100 per page. To surface recurring defects use max_stars=3 with pages=3-4: the filter is client-side."""
    return reviews(product_id, pages, with_images, max_stars, locale)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
