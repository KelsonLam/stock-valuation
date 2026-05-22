"""Stock valuation: a discounted cash flow model and a comparables cross-check.

Two independent ways to put a number on a company:

    dcf          project free cash flows, discount them at the cost of capital,
                 add a terminal value, and back out a per-share intrinsic value
    comparables  apply peer-group multiples to the company's own metrics

Neither is "the answer." The honest output is a range, plus where today's price
sits inside it, which is what the football-field chart and the recommendation
are built to show.

Modules:

    dcf          the discounted cash flow engine
    comparables  multiples-based valuation
    sensitivity  how the DCF value moves with WACC and terminal growth
    valuation    combine both methods into a range and a recommendation
    plotting      cash flow, sensitivity heatmap, and football-field charts
"""

__version__ = "0.1.0"
