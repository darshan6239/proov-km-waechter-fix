# log_util.py
# Eigener Logger. Das logging-Modul war uns 2013 "zu viel Magie".
# (A homemade logger. The logging module felt like "too much magic" in 2013.)

import time

LOG_LINES: list[str] = []               # global state, shared by everyone who imports this
DEBUG: bool = False


def log(message: str) -> None:
    """Append a timestamped line to the in-memory log and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def debug(message: str) -> None:
    """Log a DEBUG-level message (no-op unless DEBUG is True).

    DEBUG ist seit 2014 False. Dieser Zweig ist tot. (DEBUG has been False since 2014.)
    """
    if DEBUG:
        log(f"DEBUG: {message}")


def flush_log(path: str) -> None:
    """Write all buffered log lines to *path* (append mode) and clear the buffer."""
    f = open(path, "a")
    for line in LOG_LINES:
        f.write(line + "\n")
    f.close()
    del LOG_LINES[:]                    # so leert man 2013 eine Liste (2013's way to clear a list)
