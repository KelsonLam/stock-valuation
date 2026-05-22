"""Charts: the cash flow build, the sensitivity grid, and the football field.

Matplotlib only. Each function returns the Figure.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_fcf(dcf_result, title="Projected free cash flow"):
    """Projected FCF bars with their present values overlaid."""
    n = len(dcf_result.projected_fcf)
    x = np.arange(1, n + 1)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - 0.2, dcf_result.projected_fcf, width=0.4, label="Projected FCF", color="tab:blue")
    ax.bar(x + 0.2, dcf_result.pv_fcf, width=0.4, label="Present value", color="tab:orange")
    ax.set_xticks(x)
    ax.set_xlabel("Projection year")
    ax.set_ylabel("Free cash flow")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_sensitivity(grid, current_price=None, title="DCF sensitivity: WACC vs terminal growth"):
    """Heatmap of per-share value across WACC (rows) and terminal growth (cols)."""
    fig, ax = plt.subplots(figsize=(9, 6))
    data = grid.to_numpy(dtype=float)
    im = ax.imshow(data, cmap="RdYlGn", aspect="auto")
    ax.set_xticks(range(len(grid.columns)))
    ax.set_xticklabels(grid.columns)
    ax.set_yticks(range(len(grid.index)))
    ax.set_yticklabels(grid.index)
    ax.set_xlabel("Terminal growth")
    ax.set_ylabel("WACC")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not np.isnan(data[i, j]):
                ax.text(j, i, f"{data[i, j]:.0f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Intrinsic value per share")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_football_field(valuation, title="Valuation range vs current price"):
    """Per-share estimate from each method, with the current price marked."""
    methods = list(valuation.per_share_estimates.keys())
    values = list(valuation.per_share_estimates.values())
    y = np.arange(len(methods))

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(y, values, color="tab:blue", alpha=0.7)
    ax.axvline(valuation.current_price, color="tab:red", linewidth=2,
               label=f"Current price ({valuation.current_price:.0f})")
    ax.axvline(valuation.central_estimate, color="black", linestyle="--",
               label=f"Central estimate ({valuation.central_estimate:.0f})")
    ax.set_yticks(y)
    ax.set_yticklabels(methods)
    ax.set_xlabel("Value per share")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    return fig


def save_figure(fig, path: Path | str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    return path
