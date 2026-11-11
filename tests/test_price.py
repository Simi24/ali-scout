from ali_scout.models import Verdict
from ali_scout.price import check


def test_below_lowest_is_great() -> None:
    pc = check(9.83, 13.0)
    assert pc.verdict == Verdict.GREAT
    assert pc.vs_lowest_pct == -24.4


def test_within_margin_is_fair() -> None:
    assert check(10.5, 10.0).verdict == Verdict.FAIR


def test_above_margin_is_high() -> None:
    pc = check(12.0, 10.0)
    assert pc.verdict == Verdict.HIGH
    assert pc.vs_lowest_pct == 20.0


def test_missing_lowest_is_unknown() -> None:
    assert check(10.0, None).verdict == Verdict.UNKNOWN


def test_missing_lowest_with_great_tag() -> None:
    assert check(10.0, None, great_price_tag=True).verdict == Verdict.GREAT
