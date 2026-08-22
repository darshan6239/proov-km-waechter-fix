# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Nobody has cleaned it up since.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return the proportion of the service interval consumed, as a percentage.

    e.g. 12 000 km into a 15 000 km window → 80.0
    """
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True when the car has consumed >= WARN_AT_PERCENT of its service interval.

    A missing 'last_service_km' reading defaults to the current odometer value,
    which means zero km since last service (unknown history → assume just serviced).
    """
    last = car.get("last_service_km", car["odometer"])
    km_since = car["odometer"] - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return pct >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list:
    """Flag every car that needs a service and return their IDs."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
