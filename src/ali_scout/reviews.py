"""Reviews: public JSON endpoint on feedback.aliexpress.com, machine-translated into the storefront language."""

import json
import urllib.parse

from ali_scout import http, storefront
from ali_scout.models import Impression, Review, ReviewPage, StarBreakdown
from ali_scout.storefront import Locale

ENDPOINT = "https://feedback.aliexpress.com/pc/searchEvaluation.do"
PAGE_SIZE = 100  # the largest accepted value: 4 requests cover ~400 reviews
# The endpoint ignores sorting and star filters: critical reviews are found by scanning pages (max_stars).


def reviews_url(product_id: str, loc: Locale, page: int = 1, with_images: bool = False) -> str:
    params = {
        "productId": product_id,
        "lang": loc.lang,
        "country": loc.region,
        "page": page,
        "pageSize": PAGE_SIZE,
        "filter": "image" if with_images else "all",
        "sort": "complex_default",
    }
    return f"{ENDPOINT}?{urllib.parse.urlencode(params)}"


def _stats(raw: dict | None) -> StarBreakdown | None:
    if not raw:
        return None
    return StarBreakdown(
        average=raw.get("evarageStar", 0),  # sic, the API spells it this way
        total=raw.get("totalNum", 0),
        five=raw.get("fiveStarNum", 0),
        four=raw.get("fourStarNum", 0),
        three=raw.get("threeStarNum", 0),
        two=raw.get("twoStarNum", 0),
        one=raw.get("oneStarNum", 0),
    )


def _review(raw: dict) -> Review:
    return Review(
        stars=round((raw.get("buyerEval") or 0) / 20),
        date=raw.get("evalDate", ""),
        country=raw.get("buyerCountry", ""),
        text=" ".join((raw.get("buyerTranslationFeedback") or raw.get("buyerFeedback") or "").split()),
        variant=raw.get("skuInfo") or None,
        images=raw.get("images") or [],
    )


def parse_reviews(payload: dict, product_id: str, loc: Locale) -> ReviewPage:
    data = payload.get("data")
    if not isinstance(data, dict):
        raise http.BlockedError("reviews response without data: unknown product or anti-bot block")
    counts = {f["filterCode"]: f["filterCount"] for f in (data.get("filterInfo") or {}).get("filterStatistic", [])}
    return ReviewPage(
        product_id=product_id,
        url=f"{loc.base_url}/item/{product_id}.html",
        stats=_stats(data.get("productEvaluationStatistic")),
        with_images=counts.get("image"),
        impressions=[
            Impression(text=i["content"], count=i.get("num", 0), positive=i.get("emotion", 1) > 0)
            for i in data.get("impressionDTOList") or []
        ],
        page=data.get("currentPage", 1),
        total_pages=data.get("totalPage", 0),
        reviews=[_review(r) for r in data.get("evaViewList") or []],
    )


def reviews(
    product_id: str,
    pages: int = 1,
    with_images: bool = False,
    max_stars: int | None = None,
    locale: str | None = None,
    use_cache: bool = True,
) -> ReviewPage:
    """Reads up to `pages` pages of 100 and merges them; `max_stars` keeps only critical reviews (e.g. 3)."""
    loc = storefront.get(locale)
    result: ReviewPage | None = None
    for page in range(1, pages + 1):
        url = reviews_url(product_id, loc, page, with_images)
        body = http.get_text(url, use_cache=use_cache)
        current = parse_reviews(json.loads(body), product_id, loc)
        http.store(url, body)
        result = current if result is None else result.model_copy(update={"page": page, "reviews": result.reviews + current.reviews})
        if page >= current.total_pages:
            break
    assert result is not None
    if max_stars is not None:
        result = result.model_copy(update={"reviews": [r for r in result.reviews if r.stars <= max_stars]})
    return result
