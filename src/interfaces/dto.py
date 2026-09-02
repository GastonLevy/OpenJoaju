from dataclasses import dataclass, field


@dataclass
class InterfaceDTO:
    name: str
    operational_state: str
    mac_address: str
    mtu: int
    interface_type: str = "other/unknown"
    ipv4_addresses: list[str] = field(default_factory=list)
    ipv6_addresses: list[str] = field(default_factory=list)
    interface_index: int | None = None
    carrier_state: bool | None = None
    link_speed: int | None = None
    duplex: str | None = None
    rx_bytes: int | None = None
    rx_packets: int | None = None
    rx_errors: int | None = None
    rx_dropped: int | None = None
    tx_bytes: int | None = None
    tx_packets: int | None = None
    tx_errors: int | None = None
    tx_dropped: int | None = None
