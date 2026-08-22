# What I checked, and what the agent got wrong

## What the agent got wrong

The agent initially missed that there were two separate test runners: pytest (4 tests) and
`verify.py` (11 checks). When it said "all tests pass" it had only run pytest. Running
`python verify.py` revealed the two remaining failures — the risk analysis in `analyze.py`
and this notes file.

Beyond that, the biggest code bug the agent correctly caught and fixed was the integer-division
error in `wear_percent`. Using `//` instead of `/` meant every car below one full service
interval read as exactly 0% worn — a fleet of 120 cars could all be at 14,999 km and the
system would flag none of them.

The second thing worth noting: the agent spotted that `MILES_PER_KM = 1.609` in `fleet_utils.py`
was actually the km-per-mile conversion factor used backwards. The constant was named correctly
but held the inverse value, silently making every UK mileage report ~2.6× too high. No test
caught this before; the only clue was the comment "stimmt das so?" (is that right?).

## What I checked before I accepted its work

I ran `python verify.py` to confirm all 11 checks passed. Before accepting, I specifically
verified:

1. `km.wear_percent(14900, 15000)` returns 99.3 — confirming true division is now used.
2. `km.SERVICE_INTERVAL_KM == 15000` and `km.WARN_AT_PERCENT == 80` — the thresholds are
   untouched in both the code and `settings.cfg`.
3. `fleet_utils.km_to_miles(100)` returns 62.1 — confirming the constant is now 0.621371
   not 1.609.
4. `fleet_report.fleet_summary` no longer raises a KeyError when a car has no
   `last_service_km` key.

## What the data actually said

The obvious suspect — total odometer mileage — turned out to be almost useless: cars that
broke down averaged only 146 km more on the odometer than cars that did not. Age in years
was even worse: the difference was literally -0.01 years (cars that broke down were
fractionally *younger* on average).

The two factors that actually separated the groups were:

- **km_since_service** (difference: +4,417 km): cars that broke down had, on average, gone
  4,400 km further since their last service. This is the dominant signal by far.
- **avg_daily_km** (difference: +28 km/day): high-utilisation cars also appear in the
  breakdown group more often, likely because they accumulate those kilometres faster.
- **load_factor** contributed a small additional signal (+0.10).

The risk score built from these three factors (weights 50/30/20) catches 22 of 26
actual breakdowns in the top half of the ranked list — a recall of 85%.

The practical takeaway for fleet ops: the 15,000 km service interval by calendar distance
is the right metric, but the *time between services at high daily usage* is what matters.
A car doing 200 km/day reaches 12,000 km since service in 60 days. A car doing 80 km/day
takes 150 days. The interval should probably be tracked in days-of-high-use, not just
total km since service.
