"""Combine the DCF and comparables into a range and a recommendation.

No single method is trusted. The DCF gives one intrinsic estimate, the
comparables give three more, and the honest read is the range they form and
where the current price sits inside it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .dcf import run_dcf, DCFResult
from .comparables import value_from_multiples, ComparablesResult


@dataclass
class Valuation:
    dcf: DCFResult
    comparables: ComparablesResult
    current_price: float
    per_share_estimates: dict[str, float]   # every method's per-share value
    central_estimate: float                  # midpoint used for the call
    low: float
    high: float
    upside: float                            # central vs price, as a fraction
    recommendation: str


def value_company(cfg: dict) -> Valuation:
    """Run both methods from a config dict and assemble the verdict."""
    dcf = run_dcf(
        base_fcf=cfg["dcf"]["base_fcf"],
        growth_rates=cfg["dcf"]["growth_rates"],
        wacc=cfg["dcf"]["wacc"],
        terminal_growth=cfg["dcf"]["terminal_growth"],
        net_debt=cfg["net_debt"],
        shares_outstanding=cfg["shares_outstanding"],
    )
    comps = value_from_multiples(
        ebitda=cfg["comparables"]["ebitda"],
        net_income=cfg["comparables"]["net_income"],
        revenue=cfg["comparables"]["revenue"],
        shares_outstanding=cfg["shares_outstanding"],
        net_debt=cfg["net_debt"],
        peer_ev_ebitda=cfg["comparables"]["peer_ev_ebitda"],
        peer_pe=cfg["comparables"]["peer_pe"],
        peer_ps=cfg["comparables"]["peer_ps"],
    )

    estimates = {"DCF": dcf.intrinsic_value_per_share}
    estimates.update({f"Comps {k}": v for k, v in comps.per_share.items()})

    values = np.array(list(estimates.values()), dtype=float)
    central = float(np.median(values))
    low, high = float(values.min()), float(values.max())

    price = cfg["current_price"]
    upside = central / price - 1.0
    margin = cfg.get("recommendation_margin", 0.15)
    if upside > margin:
        rec = "Undervalued: the central estimate sits above the price (lean buy)."
    elif upside < -margin:
        rec = "Overvalued: the central estimate sits below the price (lean avoid)."
    else:
        rec = "Fairly valued: price is within the estimate range (hold)."

    return Valuation(
        dcf=dcf,
        comparables=comps,
        current_price=price,
        per_share_estimates=estimates,
        central_estimate=central,
        low=low,
        high=high,
        upside=upside,
        recommendation=rec,
    )
