"""Models returned by ali-scout: they are also the JSON contract for agents."""

from enum import StrEnum

from pydantic import BaseModel


class Verdict(StrEnum):
    GREAT = "great"  # at or below the 30-day low
    FAIR = "fair"  # within 10% above the low
    HIGH = "high"  # more than 10% above the low
    UNKNOWN = "unknown"  # AliExpress does not show the low


class PriceCheck(BaseModel):
    verdict: Verdict
    lowest_30d: float | None
    vs_lowest_pct: float | None  # how far the current price is above (+) or below (-) the 30-day low
    note: str


class Product(BaseModel):
    id: str
    title: str
    url: str
    image: str | None
    price: float
    currency: str
    original_price: float | None  # strikethrough price: often inflated, do not trust it alone
    discount_pct: int | None
    price_check: PriceCheck
    rating: float | None
    orders: int | None
    ship_from: str | None
    tags: list[str]


class SearchResult(BaseModel):
    query: str
    page: int
    total_results: int | None
    products: list[Product]


class StarBreakdown(BaseModel):
    average: float
    total: int
    five: int
    four: int
    three: int
    two: int
    one: int


class Impression(BaseModel):
    text: str
    count: int
    positive: bool


class Review(BaseModel):
    stars: int
    date: str
    country: str
    text: str
    variant: str | None
    images: list[str]


class ReviewPage(BaseModel):
    product_id: str
    url: str
    stats: StarBreakdown | None
    with_images: int | None
    impressions: list[Impression]
    page: int
    total_pages: int
    reviews: list[Review]
