"""Command line entry point: value a company with DCF and comparables.

Examples
--------
Value the company in config.yaml::

    python scripts/value_company.py

Save the charts as well::

    python scripts/value_company.py --save-plots
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import yaml

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from valuation.valuation import value_company
from valuation.sensitivity import sensitivity_grid
from valuation import plotting


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Value a company with DCF and comparables.")
    p.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config.yaml"))
    p.add_argument("--save-plots", action="store_true", help="Write charts to results/.")
    return p.parse_args()


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    val = value_company(cfg)

    print(f"\nValuation: {cfg.get('company', 'company')}")
    print("=" * 50)
    print(f"Current price: {val.current_price:,.2f}\n")

    print("Per-share estimates by method:")
    for method, value in val.per_share_estimates.items():
        print(f"  {method:<16} {value:,.2f}")

    print(f"\nRange: {val.low:,.2f} to {val.high:,.2f}")
    print(f"Central estimate: {val.central_estimate:,.2f}")
    print(f"Implied upside vs price: {val.upside * 100:+.1f}%")
    print(f"\nRecommendation: {val.recommendation}")

    # DCF detail: how much of the value is terminal (the fragile part).
    dcf = val.dcf
    tv_share = dcf.pv_terminal_value / dcf.enterprise_value
    print(f"\nDCF note: {tv_share * 100:.0f}% of enterprise value is the terminal value.")

    if args.save_plots:
        wacc_c = cfg["dcf"]["wacc"]
        tg_c = cfg["dcf"]["terminal_growth"]
        grid = sensitivity_grid(
            cfg["dcf"]["base_fcf"], cfg["dcf"]["growth_rates"],
            cfg["net_debt"], cfg["shares_outstanding"],
            wacc_range=np.round(np.linspace(wacc_c - 0.02, wacc_c + 0.02, 5), 4),
            terminal_growth_range=np.round(np.linspace(tg_c - 0.01, tg_c + 0.01, 5), 4),
        )
        f1 = plotting.plot_fcf(dcf)
        f2 = plotting.plot_sensitivity(grid)
        f3 = plotting.plot_football_field(val)
        for fig, name in [(f1, "fcf"), (f2, "sensitivity"), (f3, "football_field")]:
            out = plotting.save_figure(fig, f"results/{name}.png")
            print(f"Saved {out}")


if __name__ == "__main__":
    main()
