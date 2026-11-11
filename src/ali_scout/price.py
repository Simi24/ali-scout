"""Price verdict without keeping a price history.

Under the EU Omnibus directive (2019/2161) a store announcing a discount must show the lowest price of the
previous 30 days. AliExpress shows it in search results: comparing the current price with that low tells
whether the discount is real or the strikethrough price is inflated.
"""

from ali_scout.models import PriceCheck, Verdict

FAIR_MARGIN = 0.10


def check(price: float, lowest_30d: float | None, great_price_tag: bool = False) -> PriceCheck:
    if lowest_30d is None or lowest_30d <= 0:
        note = "AliExpress flags a great price for the last month" if great_price_tag else "30-day low not shown"
        return PriceCheck(verdict=Verdict.GREAT if great_price_tag else Verdict.UNKNOWN, lowest_30d=None, vs_lowest_pct=None, note=note)

    delta = round((price - lowest_30d) / lowest_30d * 100, 1)
    if delta <= 0:
        verdict, note = Verdict.GREAT, "at or below the 30-day low"
    elif delta <= FAIR_MARGIN * 100:
        verdict, note = Verdict.FAIR, "slightly above the 30-day low"
    else:
        verdict, note = Verdict.HIGH, "it sold for less in the last month"
    return PriceCheck(verdict=verdict, lowest_30d=lowest_30d, vs_lowest_pct=delta, note=note)
