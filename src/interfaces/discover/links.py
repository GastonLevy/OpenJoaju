from pathlib import Path

from ..dto import InterfaceDTO


SYS_CLASS_NET = Path("/sys/class/net")
_ARPHRD_ETHER = 1
_ARPHRD_LOOPBACK = 772


def discover_links() -> list[InterfaceDTO]:
    interfaces: list[InterfaceDTO] = []

    for interface_path in sorted(SYS_CLASS_NET.iterdir(), key=lambda path: path.name):
        statistics_path = interface_path / "statistics"
        interfaces.append(
            InterfaceDTO(
                name=interface_path.name,
                operational_state=(interface_path / "operstate").read_text().strip(),
                mac_address=(interface_path / "address").read_text().strip(),
                mtu=int((interface_path / "mtu").read_text().strip()),
                interface_type=_discover_interface_type(interface_path),
                interface_index=_read_optional_int(interface_path / "ifindex"),
                carrier_state=_read_carrier_state(interface_path / "carrier"),
                link_speed=_read_link_speed(interface_path / "speed"),
                duplex=_read_duplex(interface_path / "duplex"),
                rx_bytes=_read_optional_int(statistics_path / "rx_bytes"),
                rx_packets=_read_optional_int(statistics_path / "rx_packets"),
                rx_errors=_read_optional_int(statistics_path / "rx_errors"),
                rx_dropped=_read_optional_int(statistics_path / "rx_dropped"),
                tx_bytes=_read_optional_int(statistics_path / "tx_bytes"),
                tx_packets=_read_optional_int(statistics_path / "tx_packets"),
                tx_errors=_read_optional_int(statistics_path / "tx_errors"),
                tx_dropped=_read_optional_int(statistics_path / "tx_dropped"),
            )
        )

    return interfaces


def _discover_interface_type(interface_path: Path) -> str:
    if (interface_path / "bridge").is_dir():
        return "bridge"
    if (interface_path / "bonding").is_dir():
        return "bond"

    uevent_path = interface_path / "uevent"
    if uevent_path.exists():
        uevent = uevent_path.read_text().splitlines()
        if "DEVTYPE=vlan" in uevent:
            return "vlan"

    hardware_type = int((interface_path / "type").read_text().strip())
    if hardware_type == _ARPHRD_LOOPBACK:
        return "loopback"
    if hardware_type == _ARPHRD_ETHER:
        return "ethernet"
    return "other/unknown"


def _read_optional_text(path: Path) -> str | None:
    try:
        value = path.read_text().strip()
    except OSError:
        return None
    return value or None


def _read_optional_int(path: Path) -> int | None:
    value = _read_optional_text(path)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _read_carrier_state(path: Path) -> bool | None:
    carrier = _read_optional_int(path)
    if carrier == 1:
        return True
    if carrier == 0:
        return False
    return None


def _read_link_speed(path: Path) -> int | None:
    speed = _read_optional_int(path)
    if speed is None or speed < 0:
        return None
    return speed


def _read_duplex(path: Path) -> str | None:
    duplex = _read_optional_text(path)
    if duplex in {"full", "half"}:
        return duplex
    return None
