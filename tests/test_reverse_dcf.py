"""Tests for the reverse DCF solver."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from valuation.dcf import run_dcf
from valuation.reverse_dcf import implied_terminal_growth

BASE = dict(base_fcf=1000.0, growth_rates=[0.10, 0.10, 0.10],
            wacc=0.09, net_debt=0.0, shares_outstanding=100.0)


def test_round_trip_recovers_growth():
    # Price the company at a known terminal growth, then back it out.
    true_g = 0.035
    price = run_dcf(terminal_growth=true_g, **BASE).intrinsic_value_per_share
    recovered = implied_terminal_growth(
        price, BASE["base_fcf"], BASE["growth_rates"], BASE["wacc"],
        BASE["net_debt"], BASE["shares_outstanding"],
    )
    assert recovered == pytest.approx(true_g, abs=1e-4)


def test_unreachable_price_raises():
    # A wildly high price cannot be justified by any terminal growth below WACC.
    with pytest.raises(ValueError):
        implied_terminal_growth(
            1_000_000.0, BASE["base_fcf"], BASE["growth_rates"], BASE["wacc"],
            BASE["net_debt"], BASE["shares_outstanding"],
        )
