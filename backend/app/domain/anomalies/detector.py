"""Deterministic Isolation Forest analysis for emissions history."""

from decimal import Decimal

from sklearn.ensemble import IsolationForest


def detect_anomalies(
    observations: list[tuple[int, Decimal]],
) -> tuple[tuple[int, bool, Decimal], ...]:
    """Return anomaly labels and normalized scores for calculation totals."""

    if len(observations) < 3:
        return tuple((calculation_id, False, Decimal("0")) for calculation_id, _ in observations)
    model = IsolationForest(
        contamination="auto",
        random_state=42,
        n_estimators=100,
    )
    predictions = model.fit_predict([[float(total)] for _, total in observations])
    scores = model.decision_function([[float(total)] for _, total in observations])
    return tuple(
        (
            calculation_id,
            bool(prediction == -1),
            Decimal(str(round(float(-score), 6))),
        )
        for (calculation_id, _), prediction, score in zip(
            observations, predictions, scores, strict=True
        )
    )
