from decimal import Decimal

from app.domain.hotspots import detect_hotspots


def test_hotspots_are_ranked_and_explained() -> None:
    hotspots = detect_hotspots(
        [
            ("energy", "grid electricity", Decimal("4200"), Decimal("42")),
            ("materials", "steel", Decimal("2500"), Decimal("25")),
            ("waste", "landfill", Decimal("800"), Decimal("8")),
        ]
    )

    assert [item.rank for item in hotspots] == [1, 2, 3]
    assert [item.source for item in hotspots] == [
        "grid electricity",
        "steel",
        "landfill",
    ]
    assert [item.severity for item in hotspots] == ["high", "moderate", "low"]
    assert "grid electricity" in hotspots[0].explanation


def test_hotspot_severity_boundaries_are_explicit() -> None:
    hotspots = detect_hotspots(
        [
            ("a", "above", Decimal("31"), Decimal("30.01")),
            ("b", "boundary", Decimal("15"), Decimal("15")),
            ("c", "below", Decimal("14.99"), Decimal("14.99")),
        ]
    )

    assert [item.severity for item in hotspots] == ["high", "moderate", "low"]


def test_empty_breakdown_returns_no_hotspots() -> None:
    assert detect_hotspots([]) == ()
