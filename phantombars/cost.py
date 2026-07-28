"""Cost model. Every fill is charged, both legs. No costless backtest."""
from __future__ import annotations


class CostModel:
    """A modeled half-spread plus per-fill commission, charged round-trip.

    half_spread_bp : one-side spread cost in basis points, charged on entry and exit.
    commission_bp  : per-fill commission in basis points, charged on entry and exit.
    """

    def __init__(self, half_spread_bp: float = 1.0, commission_bp: float = 0.2):
        self.half_spread_bp = half_spread_bp
        self.commission_bp = commission_bp

    def round_trip_bp(self) -> float:
        """Total cost of one entry + one exit, in basis points."""
        return 2.0 * (self.half_spread_bp + self.commission_bp)
