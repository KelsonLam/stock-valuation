"""Charts: the cash flow build, the sensitivity grid, and the football field.

Matplotlib only. Each function returns the Figure.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

from . import viz_style


def plot_fcf(dcf_result, title="Projected free cash flow"):
    """Projected FCF bars with their present values overlaid."""
    viz_style.apply()
    n = len(dcf_result.projected_fcf)
    x = np.arange(1, n + 1)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - 0.2, dcf_result.projected_fcf, width=0.4,
          label="Projected FCF", color=viz_style.BLUE)
    ax.bar(x + 0.2, dcf_result.pv_fcf, width=0.4,
          label="Present value", color=viz_style.ORANGE)
    ax.set_xticks(x)
    ax.set_xlabel("Projection year")
    ax.set_ylabel("Free cash flow")
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def plot_sensitivity(grid, current_price=None, title="DCF sensitivity: WACC vs terminal growth"):
    """Heatmap of per-share value across WACC (rows) and terminal growth (cols).

    When the current market price is known, the colormap is centered on it:
    cells above price shade toward blue (implied upside), cells below shade
    toward red (implied downside), so the heatmap directly answers "is this
    combination of assumptions bullish or bearish versus today," not just
    "which cell is numerically bigger."
    """
    viz_style.apply()
    fig, ax = plt.subplots(figsize=(9, 6))
    data = grid.to_numpy(dtype=float)
    if current_price is not None and np.isfinite(current_price):
        finite = data[np.isfinite(data)]
        span = max(finite.max() - current_price, current_price - finite.min(), 1e-9)
        norm = TwoSlopeNorm(vmin=current_price - span, vcenter=current_price,
                            vmax=current_price + span)
        im = ax.imshow(data, cmap=viz_style.diverging_cmap(), norm=norm, aspect="auto")
    else:
        im = ax.imshow(data, cmap=viz_style.diverging_cmap(), aspect="auto")
    ax.set_xticks(range(len(grid.columns)))
    ax.set_xticklabels(grid.columns)
    ax.set_yticks(range(len(grid.index)))
    ax.set_yticklabels(grid.index)
    ax.set_xlabel("Terminal growth")
    ax.set_ylabel("WACC")
    ax.grid(visible=False)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not np.isnan(data[i, j]):
                ax.text(j, i, f"{data[i, j]:.0f}", ha="center", va="center",
                        fontsize=8, color=viz_style.INK)
    label = "Intrinsic value per share"
    if current_price is not None:
        label += f" (center = current price {current_price:.0f})"
    fig.colorbar(im, ax=ax, label=label)
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_football_field(valuation, title="Valuation range vs current price"):
    """Per-share estimate from each method, with the current price marked."""
    viz_style.apply()
    methods = list(valuation.per_share_estimates.keys())
    values = list(valuation.per_share_estimates.values())
    y = np.arange(len(methods))

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(y, values, color=viz_style.BLUE, alpha=0.8, height=0.55)
    ax.axvline(valuation.current_price, color=viz_style.RED, linewidth=2,
               label=f"Current price ({valuation.current_price:.0f})")
    ax.axvline(valuation.central_estimate, color=viz_style.INK, linestyle="--",
               linewidth=1.6,
               label=f"Central estimate ({valuation.central_estimate:.0f})")
    ax.set_yticks(y)
    ax.set_yticklabels(methods)
    ax.set_xlabel("Value per share")
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


def save_figure(fig, path: Path | str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    return path
