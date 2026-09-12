from decimal import Decimal

from app.domain.anomalies import detect_anomalies


def test_anomaly_detector_flags_outlier_history() -> None:
    results = detect_anomalies(
        [
            (1, Decimal("100")),
            (2, Decimal("102")),
            (3, Decimal("98")),
            (4, Decimal("101")),
            (5, Decimal("1000")),
        ]
    )
    assert results[-1][1] is True


def test_anomaly_detector_requires_history() -> None:
    assert detect_anomalies([(1, Decimal("100"))])[0][1] is False
