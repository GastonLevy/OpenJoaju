from dataclasses import replace

from .discover import discover_interfaces
from .dto import InterfaceDTO
from .monitor import InterfaceEvent, InterfaceEventType


class InterfaceState:
    def __init__(self) -> None:
        self._interfaces: dict[str, InterfaceDTO] = {
            interface.name: interface for interface in discover_interfaces()
        }

    def get(self, name: str) -> InterfaceDTO | None:
        return self._interfaces.get(name)

    def list(self) -> list[InterfaceDTO]:
        return list(self._interfaces.values())

    def apply_event(self, event: InterfaceEvent) -> bool:
        if event.event_type is InterfaceEventType.CREATED:
            return self._refresh_interface(event.interface_name)

        if event.event_type is InterfaceEventType.REMOVED:
            return self._interfaces.pop(event.interface_name, None) is not None

        interface = self._interfaces.get(event.interface_name)
        if interface is None:
            return False

        if event.event_type is InterfaceEventType.STATE_CHANGED:
            if (
                event.operational_state is None
                or event.operational_state == interface.operational_state
            ):
                return False
            self._interfaces[event.interface_name] = replace(
                interface, operational_state=event.operational_state
            )
            return True

        if event.event_type is InterfaceEventType.IPV4_ADDRESS_ADDED:
            return self._add_address(interface, event.address, ipv6=False)
        if event.event_type is InterfaceEventType.IPV4_ADDRESS_REMOVED:
            return self._remove_address(interface, event.address, ipv6=False)
        if event.event_type is InterfaceEventType.IPV6_ADDRESS_ADDED:
            return self._add_address(interface, event.address, ipv6=True)
        if event.event_type is InterfaceEventType.IPV6_ADDRESS_REMOVED:
            return self._remove_address(interface, event.address, ipv6=True)

        return False

    def resynchronize(self) -> bool:
        interfaces = {
            interface.name: interface for interface in discover_interfaces()
        }
        if interfaces == self._interfaces:
            return False
        self._interfaces = interfaces
        return True

    def _refresh_interface(self, name: str) -> bool:
        discovered = next(
            (interface for interface in discover_interfaces() if interface.name == name),
            None,
        )
        if discovered is None or discovered == self._interfaces.get(name):
            return False
        self._interfaces[name] = discovered
        return True

    def _add_address(
        self, interface: InterfaceDTO, address: str | None, *, ipv6: bool
    ) -> bool:
        addresses = (
            interface.ipv6_addresses if ipv6 else interface.ipv4_addresses
        )
        if address is None or address in addresses:
            return False

        field_name = "ipv6_addresses" if ipv6 else "ipv4_addresses"
        self._interfaces[interface.name] = replace(
            interface, **{field_name: [*addresses, address]}
        )
        return True

    def _remove_address(
        self, interface: InterfaceDTO, address: str | None, *, ipv6: bool
    ) -> bool:
        addresses = (
            interface.ipv6_addresses if ipv6 else interface.ipv4_addresses
        )
        if address is None or address not in addresses:
            return False

        field_name = "ipv6_addresses" if ipv6 else "ipv4_addresses"
        self._interfaces[interface.name] = replace(
            interface,
            **{field_name: [item for item in addresses if item != address]},
        )
        return True
