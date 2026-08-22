# test_fleet_report.py
from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_summary_does_not_crash_without_last_service_km():
    # A car with no "last_service_km" key must not raise a KeyError; it should
    # be treated as having zero km since last service (unknown → assume just serviced).
    fleet_no_reading = [
        {"id": "VOS-7788", "odometer": 92000},
        {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    ]
    result = fleet_summary(fleet_no_reading)
    # VOS-7788: 0 km since service → not due. VOS-4471: ~99% worn → due.
    assert result["due"] == 1
    assert result["count"] == 2
