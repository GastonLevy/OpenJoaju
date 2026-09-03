from dataclasses import dataclass


@dataclass
class NeighborDTO:
    ip_address: str
    mac_address: str | None
    interface: str | None
    interface_index: int
    family: str
    state: str
