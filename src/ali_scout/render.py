"""Compact text output, readable by a person and by an LLM without wasting tokens."""

from ali_scout.models import Product, ReviewPage, SearchResult

_VERDICT = {"great": "GREAT", "fair": "FAIR", "high": "HIGH", "unknown": "?"}


def _price_line(p: Product) -> str:
    pc = p.price_check
    lowest = f"30d low {pc.lowest_30d:.2f} ({pc.vs_lowest_pct:+.0f}%)" if pc.lowest_30d is not None else "30d low n/a"
    return f"{p.price:.2f} {p.currency} [{_VERDICT[pc.verdict]}] {lowest}"


def product(p: Product) -> str:
    stats = " · ".join(
        s
        for s in [
            f"★{p.rating}" if p.rating else "",
            f"{p.orders} orders" if p.orders else "",
            f"ships from {p.ship_from}" if p.ship_from else "",
        ]
        if s
    )
    tags = f"\n    {' | '.join(p.tags)}" if p.tags else ""
    return f"- [{p.id}] {p.title}\n    {_price_line(p)} · {stats}\n    {p.url}{tags}"


def search(r: SearchResult) -> str:
    head = f"'{r.query}' page {r.page}" + (f" ({r.total_results} results)" if r.total_results else "")
    return "\n".join([head, *(product(p) for p in r.products)])


def reviews(r: ReviewPage) -> str:
    lines = [r.url]
    if r.stats:
        s = r.stats
        lines.append(f"★{s.average} from {s.total} reviews · 5★ {s.five} · 4★ {s.four} · 3★ {s.three} · 2★ {s.two} · 1★ {s.one}")
    if r.impressions:
        lines.append("Impressions: " + ", ".join(f"{i.text} ({i.count}{'' if i.positive else ', negative'})" for i in r.impressions))
    for rv in (rv for rv in r.reviews if rv.text):  # star-only reviews count in the stats, not here
        variant = f" [{rv.variant}]" if rv.variant else ""
        photos = f" ({len(rv.images)} photos)" if rv.images else ""
        lines.append(f"- {rv.stars}★ {rv.date} {rv.country}{variant}{photos}: {rv.text}")
    return "\n".join(lines)
