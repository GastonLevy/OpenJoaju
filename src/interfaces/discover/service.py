from dataclasses import replace

from ..dto import InterfaceDTO
from .addresses import discover_addresses
from .links import discover_links


def discover_interfaces() -> list[InterfaceDTO]:
    addresses = discover_addresses()
    interfaces: list[InterfaceDTO] = []

    for interface in discover_links():
        ipv4_addresses, ipv6_addresses = addresses.get(interface.name, ([], []))

        interfaces.append(
            replace(
                interface,
                ipv4_addresses=ipv4_addresses,
                ipv6_addresses=ipv6_addresses,
            )
        )

    return interfaces