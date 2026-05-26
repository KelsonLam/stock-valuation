"""Edge-case and validation tests for the valuation engine."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from valuation.dcf import run_dcf
from valuation.comparables import value_from_multiples


def test_dcf_rejects_zero_shares():
    with pytest.raises(ValueError):
        run_dcf(100.0, [0.1], wacc=0.10, terminal_growth=0.02,
                net_debt=0.0, shares_outstanding=0.0)


def test_comparables_rejects_zero_shares():
    with pytest.raises(ValueError):
        value_from_multiples(1000, 500, 4000, 0.0, 0.0, 10, 15, 2)


def test_net_cash_raises_equity_above_enterprise():
    # Negative net debt (net cash) makes equity value exceed enterprise value.
    res = run_dcf(1000.0, [0.08, 0.08], wacc=0.10, terminal_growth=0.03,
                  net_debt=-5000.0, shares_outstanding=100.0)
    assert res.equity_value > res.enterprise_value


def test_higher_terminal_growth_raises_value():
    base = dict(base_fcf=1000.0, growth_rates=[0.08, 0.08], wacc=0.10,
                net_debt=0.0, shares_outstanding=100.0)
    low = run_dcf(terminal_growth=0.01, **base).intrinsic_value_per_share
    high = run_dcf(terminal_growth=0.04, **base).intrinsic_value_per_share
    assert high > low
