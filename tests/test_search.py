from pathlib import Path

import pytest

from ali_scout import storefront
from ali_scout.http import BlockedError
from ali_scout.models import Verdict
from ali_scout.search import Sort, _number, parse_search, search_url

FIXTURE = Path(__file__).parent / "fixtures" / "search.html"
IT = storefront.get("it")


@pytest.fixture
def result():
    return parse_search(FIXTURE.read_text(encoding="utf-8"), "sonoff snzb-02d", IT)


def test_parses_products(result) -> None:
    assert result.total_results == 187
    assert len(result.products) == 4


def test_first_product_fields(result) -> None:
    p = result.products[0]
    assert p.id == "1005005372282766"
    assert p.url == "https://it.aliexpress.com/item/1005005372282766.html"
    assert p.price == 9.83
    assert p.original_price == 13.0
    assert p.discount_pct == 24
    assert p.rating == 4.9
    assert p.orders == 3536
    assert p.ship_from == "CN"
    assert p.price_check.lowest_30d == 13.0
    assert p.price_check.verdict == Verdict.GREAT
    assert "Ottimo prezzo nell'ultimo mese" in p.tags
    assert not any("30 giorni" in t for t in p.tags)


def test_product_without_lowest(result) -> None:
    p = result.products[2]
    assert p.price_check.verdict == Verdict.UNKNOWN
    assert p.rating is None


def test_page_without_items_is_blocked() -> None:
    with pytest.raises(BlockedError):
        parse_search("<html>captcha</html>", "x", IT)


def test_search_url() -> None:
    assert search_url("sonoff snzb-02d", IT) == "https://it.aliexpress.com/w/wholesale-sonoff-snzb-02d.html"
    assert search_url("gloves", storefront.get("us"), Sort.ORDERS, 2) == (
        "https://www.aliexpress.com/w/wholesale-gloves.html?SortType=total_tranpro_desc&page=2"
    )


@pytest.mark.parametrize(("text", "value"), [("13", 13.0), ("12,42", 12.42), ("1.234,56", 1234.56), ("1,234.56", 1234.56), ("9.99", 9.99)])
def test_number_formats(text: str, value: float) -> None:
    assert _number(text) == value


def test_unknown_locale() -> None:
    with pytest.raises(ValueError):
        storefront.get("xx")
