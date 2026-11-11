"""Product search: the search page already embeds the results as JSON (itemList), so they only need extracting."""

import json
import re
import urllib.parse
from enum import StrEnum

from ali_scout import http, price, storefront
from ali_scout.models import Product, SearchResult
from ali_scout.storefront import Locale

_DECODER = json.JSONDecoder()
_ITEMS_RE = re.compile(r'"itemList"\s*:\s*\{\s*"content"\s*:\s*')
_PAGE_INFO_RE = re.compile(r'"pageInfo"\s*:\s*')
_NUMBER_RE = re.compile(r"\d[\d.,]*")
_TAG_RE = re.compile(r"<[^>]+>")
_LOWEST_TAG = "lowestprice"  # tag ids like "common_other_lowestprice_PL_atm", same in every language
_GREAT_PRICE_TAG = "great_price"


class Sort(StrEnum):
    BEST = "default"
    ORDERS = "total_tranpro_desc"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NEWEST = "create_desc"


def search_url(query: str, loc: Locale, sort: Sort = Sort.BEST, page: int = 1) -> str:
    slug = urllib.parse.quote(query.strip().replace(" ", "-"))
    params = {k: v for k, v in {"SortType": sort.value if sort != Sort.BEST else None, "page": page if page > 1 else None}.items() if v}
    return f"{loc.base_url}/w/wholesale-{slug}.html" + (f"?{urllib.parse.urlencode(params)}" if params else "")


def _json_after(html: str, marker: re.Pattern[str]) -> object | None:
    m = marker.search(html)
    if not m:
        return None
    value, _ = _DECODER.raw_decode(html, m.end())
    return value


def _number(text: str) -> float | None:
    """'1.234,56' / '13' / '12,42' / '1,234.56' -> float."""
    text = text.strip().rstrip(".,")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".") if text.rfind(",") > text.rfind(".") else text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def _texts(item: dict) -> list[tuple[str, str]]:
    """(tag id, readable text) of the selling points: badges, 30-day low, 'great price'."""
    out = []
    for sp in item.get("sellingPoints") or []:
        for m in sp.get("materials") or []:
            value = _TAG_RE.sub("", str(m.get("value", ""))).strip()
            if m.get("type") == "TEXT" and value and not value.startswith("#") and re.search(r"[^\W\d_]", value):
                out.append((sp.get("sellingPointTagId", ""), value))
    return out


def _lowest_30d(texts: list[tuple[str, str]]) -> float | None:
    """The text reads e.g. 'Lowest price in the last 30 days: 13€': the price is the last number."""
    for tag, text in texts:
        if _LOWEST_TAG in tag and (numbers := _NUMBER_RE.findall(text)):
            return _number(numbers[-1])
    return None


def _trace(item: dict) -> dict:
    raw = (item.get("trace") or {}).get("pdpParams", {}).get("pdp_cdi")
    try:
        return json.loads(urllib.parse.unquote(raw)) if raw else {}
    except json.JSONDecodeError:
        return {}


def _original_price(item: dict) -> float | None:
    """The strikethrough price sits in the pdp_npi parameter: '6@dis!EUR!<list>!<sale>!...'."""
    npi = urllib.parse.unquote((item.get("trace") or {}).get("pdpParams", {}).get("pdp_npi", ""))
    parts = npi.split("!")
    return _number(parts[2]) if len(parts) > 3 and parts[2] else None


def parse_product(item: dict, loc: Locale) -> Product | None:
    sale = (item.get("prices") or {}).get("salePrice") or {}
    if "minPrice" not in sale:
        return None
    pid = str(item.get("productId") or item.get("redirectedId"))
    texts = _texts(item)
    great_tag = any(tag == _GREAT_PRICE_TAG for tag, _ in texts)
    trace = _trace(item)
    image = (item.get("image") or {}).get("imgUrl")
    orders = trace.get("order")
    return Product(
        id=pid,
        title=item.get("title", {}).get("displayTitle", ""),
        url=f"{loc.base_url}/item/{pid}.html",
        image=f"https:{image}" if image and image.startswith("//") else image,
        price=sale["minPrice"],
        currency=sale.get("currencyCode", loc.currency),
        original_price=_original_price(item),
        discount_pct=sale.get("discount"),
        price_check=price.check(sale["minPrice"], _lowest_30d(texts), great_tag),
        rating=(item.get("evaluation") or {}).get("starRating"),
        orders=int(orders) if str(orders or "").isdigit() else None,
        ship_from=trace.get("shipFrom"),
        tags=[text for tag, text in texts if _LOWEST_TAG not in tag],
    )


def parse_search(html: str, query: str, loc: Locale, page: int = 1) -> SearchResult:
    items = _json_after(html, _ITEMS_RE)
    if items is None:
        raise http.BlockedError("no results in the page: probably an anti-bot block, retry in a few minutes")
    info = _json_after(html, _PAGE_INFO_RE) or {}
    products = [p for it in items if (p := parse_product(it, loc))]
    return SearchResult(query=query, page=page, total_results=info.get("totalResults"), products=products)


def search(query: str, sort: Sort = Sort.BEST, page: int = 1, locale: str | None = None, use_cache: bool = True) -> SearchResult:
    loc = storefront.get(locale)
    url = search_url(query, loc, sort, page)
    html = http.get_text(url, {"Accept-Language": loc.accept_language, "Cookie": loc.cookie}, use_cache)
    result = parse_search(html, query, loc, page)
    http.store(url, html)
    return result


def filter_products(result: SearchResult, limit: int, min_rating: float | None = None, min_orders: int | None = None) -> SearchResult:
    products = [
        p
        for p in result.products
        if (min_rating is None or (p.rating or 0) >= min_rating) and (min_orders is None or (p.orders or 0) >= min_orders)
    ]
    return result.model_copy(update={"products": products[:limit]})
