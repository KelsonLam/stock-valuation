"""Relative valuation: what the market pays for similar companies.

A DCF asks what a company is worth on its own cash flows. Comparables ask a
different question: if peers trade at 18 times EBITDA, what would this company be
worth at the same multiple? It is faster, it is anchored to real market prices,
and it is only as good as the peer set you choose.

Three standard multiples are supported, and they attach to value at different
points in the capital structure, which matters:

    EV / EBITDA   gives an enterprise value, so subtract net debt for equity
    P / E         gives an equity value directly
    P / S         gives an equity value directly (price-to-sales)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ComparablesResult:
    per_share: dict[str, float]    # implied per-share value by multiple
    average_per_share: float


def value_from_multiples(
    ebitda: float,
    net_income: float,
    revenue: float,
    shares_outstanding: float,
    net_debt: float,
    peer_ev_ebitda: float,
    peer_pe: float,
    peer_ps: float,
) -> ComparablesResult:
    """Apply peer multiples to the target's metrics for an implied per-share value."""
    if shares_outstanding <= 0:
        raise ValueError("shares_outstanding must be positive.")

    per_share: dict[str, float] = {}

    # EV/EBITDA -> enterprise value -> equity value -> per share
    ev = peer_ev_ebitda * ebitda
    per_share["EV/EBITDA"] = (ev - net_debt) / shares_outstanding

    # P/E -> equity value directly
    per_share["P/E"] = (peer_pe * net_income) / shares_outstanding

    # P/S -> equity value directly
    per_share["P/S"] = (peer_ps * revenue) / shares_outstanding

    average = sum(per_share.values()) / len(per_share)
    return ComparablesResult(per_share=per_share, average_per_share=average)
