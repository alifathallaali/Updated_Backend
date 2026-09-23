# Chart Prioritization

Display order is selected deterministically from the exercise family and declared chart patterns.
The prioritizer adds `presentationPriority` metadata (`score`, `rank`, `role`) to ChartSpec copies.
It never changes chart data, metrics, evidence or calculations.

Examples:
- Forecast → forecast/actual-vs-forecast before generic market trend
- Scenario → scenario comparison
- Launch → risk/score
- Finance → variance/waterfall when those visuals exist
- Sales → achievement/ranking
- Inventory → risk/cover
