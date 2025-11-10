import datetime

def print_debug(msg: str) -> None:
    print(f"[{datetime.datetime.now():%H:%M:%S}] [DEBUG] {msg}")


def print_error(msg: str) -> None:
    print(f"[{datetime.datetime.now():%H:%M:%S}] [ERROR] {msg}")
