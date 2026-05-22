"""Tests for the DCF math, comparables, sensitivity, and the recommendation.

All deterministic and offline. Several checks use hand-computed values.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from valuation.dcf import run_dcf, project_fcf
from valuation.comparables import value_from_multiples
from valuation.sensitivity import sensitivity_grid
from valuation.valuation import value_company


def test_project_fcf_compounds():
    fcf = project_fcf(100.0, [0.10, 0.10])
    assert fcf[0] == pytest.approx(110.0)
    assert fcf[1] == pytest.approx(121.0)


def test_dcf_matches_hand_calc():
    # One year of FCF, simple numbers, so the whole thing is checkable by hand.
    # base 100, one year at 10% growth -> FCF1 = 110.
    # WACC 10%, terminal growth 0% -> TV = 110 * 1.0 / 0.10 = 1100.
    # PV FCF1 = 110 / 1.1 = 100; PV TV = 1100 / 1.1 = 1000.
    # EV = 1100; net debt 100 -> equity 1000; 10 shares -> 100 per share.
    res = run_dcf(
        base_fcf=100.0, growth_rates=[0.10], wacc=0.10,
        terminal_growth=0.0, net_debt=100.0, shares_outstanding=10.0,
    )
    assert res.pv_fcf[0] == pytest.approx(100.0)
    assert res.terminal_value == pytest.approx(1100.0)
    assert res.pv_terminal_value == pytest.approx(1000.0)
    assert res.enterprise_value == pytest.approx(1100.0)
    assert res.equity_value == pytest.approx(1000.0)
    assert res.intrinsic_value_per_share == pytest.approx(100.0)


def test_dcf_rejects_wacc_below_terminal_growth():
    with pytest.raises(ValueError):
        run_dcf(100.0, [0.05], wacc=0.03, terminal_growth=0.04,
                net_debt=0.0, shares_outstanding=10.0)


def test_higher_wacc_lowers_value():
    kw = dict(base_fcf=100.0, growth_rates=[0.08, 0.08, 0.08],
              terminal_growth=0.02, net_debt=0.0, shares_outstanding=10.0)
    low = run_dcf(wacc=0.08, **kw).intrinsic_value_per_share
    high = run_dcf(wacc=0.12, **kw).intrinsic_value_per_share
    assert high < low


def test_comparables_formulas():
    res = value_from_multiples(
        ebitda=1000.0, net_income=500.0, revenue=4000.0,
        shares_outstanding=100.0, net_debt=200.0,
        peer_ev_ebitda=10.0, peer_pe=15.0, peer_ps=2.0,
    )
    # EV/EBITDA: 10*1000 = 10000 EV; equity 9800; /100 = 98
    assert res.per_share["EV/EBITDA"] == pytest.approx(98.0)
    # P/E: 15*500 = 7500; /100 = 75
    assert res.per_share["P/E"] == pytest.approx(75.0)
    # P/S: 2*4000 = 8000; /100 = 80
    assert res.per_share["P/S"] == pytest.approx(80.0)
    assert res.average_per_share == pytest.approx((98 + 75 + 80) / 3)


def test_sensitivity_grid_shape_and_nan():
    grid = sensitivity_grid(
        base_fcf=100.0, growth_rates=[0.05], net_debt=0.0, shares_outstanding=10.0,
        wacc_range=[0.04, 0.08], terminal_growth_range=[0.03, 0.05],
    )
    assert grid.shape == (2, 2)
    # WACC 0.04 with terminal growth 0.05 is invalid -> NaN.
    assert np.isnan(grid.iloc[0, 1])


def test_recommendation_undervalued():
    cfg = {
        "current_price": 50.0, "shares_outstanding": 100.0, "net_debt": 0.0,
        "recommendation_margin": 0.15,
        "dcf": {"base_fcf": 500.0, "growth_rates": [0.10, 0.10, 0.10],
                "wacc": 0.09, "terminal_growth": 0.03},
        "comparables": {"ebitda": 900.0, "net_income": 600.0, "revenue": 5000.0,
                        "peer_ev_ebitda": 15.0, "peer_pe": 20.0, "peer_ps": 2.5},
    }
    val = value_company(cfg)
    # Estimates should land well above 50, so the call is undervalued.
    assert val.central_estimate > 50.0
    assert "Undervalued" in val.recommendation
