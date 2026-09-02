import sys

from .dto import InterfaceDTO


_GREEN = "\033[32m"
_RED = "\033[31m"
_RESET = "\033[0m"
_TYPE_PRIORITY = {
    "loopback": 0,
    "ethernet": 1,
    "bond": 2,
    "vlan": 3,
    "bridge": 4,
    "other/unknown": 5,
}


def print_interfaces(interfaces: list[InterfaceDTO]) -> None:
    for interface in _sorted_interfaces(interfaces):
        print("------------------------------")
        print(f"Interface: {interface.name}")
        print(f"Type:      {interface.interface_type}")
        print(f"State:     {_format_state(interface.operational_state)}")
        print(f"MAC:       {interface.mac_address}")
        print(f"IPv4:      {_format_addresses(interface.ipv4_addresses)}")
        print(f"IPv6:      {_format_addresses(interface.ipv6_addresses)}")
        print("------------------------------")


def print_interface(interface: InterfaceDTO) -> None:
    print("------------------------------")
    print(f"Interface:  {interface.name}")
    print(f"Type:       {interface.interface_type}")
    print(f"State:      {_format_state(interface.operational_state)}")
    print(f"MAC:        {interface.mac_address}")
    print(f"MTU:        {interface.mtu}")
    print(f"Index:      {_format_optional(interface.interface_index)}")
    print(f"Carrier:    {_format_carrier(interface.carrier_state)}")
    print(f"Link speed: {_format_speed(interface.link_speed)}")
    print(f"Duplex:     {_format_optional(interface.duplex)}")
    print()
    print(f"IPv4:       {_format_addresses(interface.ipv4_addresses)}")
    print(f"IPv6:       {_format_addresses(interface.ipv6_addresses)}")
    print()
    print("RX:")
    print(f"  Bytes:   {_format_optional(interface.rx_bytes)}")
    print(f"  Packets: {_format_optional(interface.rx_packets)}")
    print(f"  Errors:  {_format_optional(interface.rx_errors)}")
    print(f"  Dropped: {_format_optional(interface.rx_dropped)}")
    print("TX:")
    print(f"  Bytes:   {_format_optional(interface.tx_bytes)}")
    print(f"  Packets: {_format_optional(interface.tx_packets)}")
    print(f"  Errors:  {_format_optional(interface.tx_errors)}")
    print(f"  Dropped: {_format_optional(interface.tx_dropped)}")
    print("------------------------------")


def print_interface_names(interfaces: list[InterfaceDTO]) -> None:
    for interface in _sorted_interfaces(interfaces):
        print(interface.name)


def print_mac_addresses(interfaces: list[InterfaceDTO]) -> None:
    for interface in _sorted_interfaces(interfaces):
        print(interface.mac_address)


def _format_addresses(addresses: list[str]) -> str:
    return ", ".join(addresses) if addresses else "-"


def _format_optional(value: object | None) -> str:
    return str(value) if value is not None else "-"


def _format_carrier(carrier_state: bool | None) -> str:
    if carrier_state is None:
        return "-"
    return "up" if carrier_state else "down"


def _format_speed(link_speed: int | None) -> str:
    return f"{link_speed} Mbps" if link_speed is not None else "-"


def _sorted_interfaces(interfaces: list[InterfaceDTO]) -> list[InterfaceDTO]:
    return sorted(
        interfaces,
        key=lambda interface: (
            _TYPE_PRIORITY.get(interface.interface_type, _TYPE_PRIORITY["other/unknown"]),
            interface.name,
        ),
    )


def _format_state(state: str) -> str:
    if not sys.stdout.isatty():
        return state
    if state == "up":
        return f"{_GREEN}{state}{_RESET}"
    if state == "down":
        return f"{_RED}{state}{_RESET}"
    return state
