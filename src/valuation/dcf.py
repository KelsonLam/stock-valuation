"""The discounted cash flow engine.

Intrinsic value rests on one idea: a company is worth the cash it will hand its
owners over its life, discounted back because a dollar later is worth less than
a dollar now. Concretely:

    1. Project free cash flow for a handful of years using growth assumptions.
    2. Discount each year's FCF to today at the weighted average cost of capital.
    3. Capture everything past the projection window in a terminal value (Gordon
       growth), and discount that back too.
    4. Sum to enterprise value, subtract net debt to get equity value, divide by
       shares for a per-share intrinsic value.

The terminal value usually dominates, which is the model's great weakness: a
huge share of the answer rests on two assumptions (the perpetual growth rate and
the discount rate). The sensitivity module exists precisely because of that.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class DCFResult:
    projected_fcf: np.ndarray      # FCF for each projected year
    pv_fcf: np.ndarray             # present value of each year's FCF
    terminal_value: float          # undiscounted terminal value at the horizon
    pv_terminal_value: float        # present value of the terminal value
    enterprise_value: float
    equity_value: float
    intrinsic_value_per_share: float


def project_fcf(base_fcf: float, growth_rates) -> np.ndarray:
    """Grow the base free cash flow forward by the per-year growth rates."""
    factors = np.cumprod(1.0 + np.asarray(growth_rates, dtype=float))
    return base_fcf * factors


def run_dcf(
    base_fcf: float,
    growth_rates,
    wacc: float,
    terminal_growth: float,
    net_debt: float,
    shares_outstanding: float,
) -> DCFResult:
    """Run a full DCF and return every intermediate piece."""
    if wacc <= terminal_growth:
        raise ValueError(
            "WACC must exceed the terminal growth rate, or the terminal value "
            "is infinite (and the model is meaningless)."
        )
    if shares_outstanding <= 0:
        raise ValueError("shares_outstanding must be positive.")

    fcf = project_fcf(base_fcf, growth_rates)
    years = np.arange(1, len(fcf) + 1)
    discount = (1.0 + wacc) ** years
    pv_fcf = fcf / discount

    # Gordon growth terminal value on the final projected year.
    terminal_value = fcf[-1] * (1.0 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal_value = terminal_value / discount[-1]

    enterprise_value = pv_fcf.sum() + pv_terminal_value
    equity_value = enterprise_value - net_debt
    per_share = equity_value / shares_outstanding

    return DCFResult(
        projected_fcf=fcf,
        pv_fcf=pv_fcf,
        terminal_value=terminal_value,
        pv_terminal_value=pv_terminal_value,
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        intrinsic_value_per_share=per_share,
    )
