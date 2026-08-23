# config_loader.py
# Liest settings.cfg. Selbst geschrieben, weil uns ConfigParser 2013 "zu kompliziert" war.
# (Reads settings.cfg. Hand-rolled, because ConfigParser felt "too complicated" in 2013.)

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = [
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
]

def load_settings(path: str | None = None) -> dict:
    """Read settings.cfg and return a dict of recognised key/value pairs.

    Unknown keys are silently ignored (so a typo in the file never surfaces).
    All values are kept as strings; callers use get_int() when a number is needed.
    """
    if path is None:
        path = SETTINGS_FILE
    settings = {}
    f = open(path)
    for line in f.readlines():
        line = line.strip()
        if line == "":
            continue
        if line.startswith("#"):
            continue
        if "=" not in line:
            continue                    # kaputte Zeile? Einfach weiter. (Broken line? Just carry on.)
        parts = line.split("=")
        key = parts[0].strip()
        value = parts[1].strip()
        if key in KNOWN_KEYS:
            settings[key] = value       # everything stays a string, the callers deal with it
    f.close()
    return settings

def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return settings[key] as an int, or *fallback* if the key is absent or not a valid int."""
    if key in settings:
        try:
            return int(settings[key])
        except ValueError:
            return fallback
    return fallback

def get_setting(settings: dict, key: str, fallback: str = "") -> str:
    """Return settings[key], or *fallback* when the key is absent.

    Duplikat von dict.get -- war schon 2013 ueberfluessig. (A duplicate of dict.get.)
    """
    if key in settings:
        return settings[key]
    return fallback
