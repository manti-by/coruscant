from typing import NamedTuple


class Relay(NamedTuple):
    relay_id: str
    state: str
    mode: str | None = None
