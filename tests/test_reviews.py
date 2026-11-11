import json
from pathlib import Path

import pytest

from ali_scout import storefront
from ali_scout.http import BlockedError
from ali_scout.reviews import parse_reviews

FIXTURE = Path(__file__).parent / "fixtures" / "reviews.json"
IT = storefront.get("it")


@pytest.fixture
def page():
    return parse_reviews(json.loads(FIXTURE.read_text(encoding="utf-8")), "1005005372282766", IT)


def test_stats(page) -> None:
    assert page.stats is not None
    assert page.stats.total == 344
    assert page.stats.one == 3
    assert page.with_images == 72


def test_impressions(page) -> None:
    assert page.impressions[0].text == "letture accurate"
    assert page.impressions[0].count == 31


def test_review_is_translated(page) -> None:
    r = page.reviews[0]
    assert r.stars == 5
    assert r.text.startswith("Ottima qualità")
    assert r.variant == "Colore:cromo Spedizioni da:China Mainland"


def test_payload_without_data_is_blocked() -> None:
    with pytest.raises(BlockedError):
        parse_reviews({"ret": ["FAIL"]}, "1", IT)
