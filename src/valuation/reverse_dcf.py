"""Reverse DCF: what does today's price actually assume?

A normal DCF takes assumptions and produces a value. A reverse DCF runs it
backwards: hold everything fixed except one assumption, and solve for the value
of that assumption which makes the model output equal the current market price.
It reframes the question from "what is it worth" to "what would have to be true
for today's price to be fair," which is often the more honest way to argue about
a valuation.

This solves for the implied perpetual (terminal) growth rate, since the per-share
value rises monotonically with it, so a simple bisection converges cleanly.
"""

from __future__ import annotations

from .dcf import run_dcf


def implied_terminal_growth(
    target_price: float,
    base_fcf: float,
    growth_rates,
    wacc: float,
    net_debt: float,
    shares_outstanding: float,
    tol: float = 1e-6,
    max_iter: int = 200,
) -> float:
    """Solve for the terminal growth rate that justifies ``target_price``.

    Returns the implied rate. Raises if the price cannot be reached for any
    terminal growth strictly below WACC (the model's hard ceiling).
    """
    low, high = -0.50, wacc - 1e-4
    if low >= high:
        raise ValueError("WACC is too low to admit a valid terminal growth range.")

    def per_share(g: float) -> float:
        return run_dcf(
            base_fcf, growth_rates, wacc, g, net_debt, shares_outstanding
        ).intrinsic_value_per_share

    if per_share(low) > target_price or per_share(high) < target_price:
        raise ValueError(
            "The price is not reachable for any terminal growth below WACC. "
            "The market may be pricing in different cash flows or discount rate."
        )

    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        value = per_share(mid)
        if abs(value - target_price) < tol:
            return mid
        if value < target_price:
            low = mid
        else:
            high = mid
    return 0.5 * (low + high)
