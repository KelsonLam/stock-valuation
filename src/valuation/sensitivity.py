"""How much the DCF answer depends on its two most fragile assumptions.

The terminal value usually drives most of a DCF, and it is governed by the
discount rate (WACC) and the perpetual growth rate. A small change in either can
swing the per-share value a lot. This module sweeps both across a grid so you can
see the spread instead of trusting a single point estimate.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .dcf import run_dcf


def sensitivity_grid(
    base_fcf: float,
    growth_rates,
    net_debt: float,
    shares_outstanding: float,
    wacc_range,
    terminal_growth_range,
) -> pd.DataFrame:
    """Per-share intrinsic value for each (WACC, terminal growth) pair.

    Rows are WACC, columns are terminal growth. Combinations where WACC does not
    exceed terminal growth are left as NaN (the model is undefined there).
    """
    wacc_range = np.asarray(wacc_range, dtype=float)
    tg_range = np.asarray(terminal_growth_range, dtype=float)
    grid = np.full((len(wacc_range), len(tg_range)), np.nan)

    for i, w in enumerate(wacc_range):
        for j, g in enumerate(tg_range):
            if w <= g:
                continue
            grid[i, j] = run_dcf(
                base_fcf, growth_rates, w, g, net_debt, shares_outstanding
            ).intrinsic_value_per_share

    return pd.DataFrame(
        grid,
        index=[f"{w:.1%}" for w in wacc_range],
        columns=[f"{g:.1%}" for g in tg_range],
    )
