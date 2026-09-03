import errno
import socket
import struct
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum

from .discover.links import discover_links


_NETLINK_ROUTE = 0
_RTM_NEWLINK = 16
_RTM_DELLINK = 17
_RTM_NEWADDR = 20
_RTM_DELADDR = 21
_NLMSG_ERROR = 2
_NLMSG_DONE = 3
_NLMSG_OVERRUN = 4
_NLM_F_DUMP_INTR = 0x10

_RTMGRP_LINK = 1
_RTMGRP_IPV4_IFADDR = 0x10
_RTMGRP_IPV6_IFADDR = 0x100

_IFLA_IFNAME = 3
_IFLA_OPERSTATE = 16
_IFA_ADDRESS = 1
_IFA_LOCAL = 2

_IFF_UP = 0x1
_IFF_RUNNING = 0x40
_IFF_LOWER_UP = 0x10000
_IFF_DORMANT = 0x20000
_STATE_FLAGS = _IFF_UP | _IFF_RUNNING | _IFF_LOWER_UP | _IFF_DORMANT

_OPERSTATES = {
    0: "unknown",
    1: "notpresent",
    2: "down",
    3: "lowerlayerdown",
    4: "testing",
    5: "dormant",
    6: "up",
}


class InterfaceEventType(StrEnum):
    CREATED = "interface_created"
    REMOVED = "interface_removed"
    STATE_CHANGED = "interface_state_changed"
    IPV4_ADDRESS_ADDED = "ipv4_address_added"
    IPV4_ADDRESS_REMOVED = "ipv4_address_removed"
    IPV6_ADDRESS_ADDED = "ipv6_address_added"
    IPV6_ADDRESS_REMOVED = "ipv6_address_removed"


class InterfaceSynchronizationError(OSError):
    pass


@dataclass(frozen=True)
class InterfaceEvent:
    event_type: InterfaceEventType
    interface_name: str
    address: str | None = None
    operational_state: str | None = None


def monitor_events() -> Iterator[InterfaceEvent]:
    """Yield interface and address changes from Linux route Netlink."""
    groups = _RTMGRP_LINK | _RTMGRP_IPV4_IFADDR | _RTMGRP_IPV6_IFADDR

    with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_ROUTE) as netlink:
        netlink.bind((0, groups))

        interface_names: dict[int, str] = {}
        operational_states: dict[int, str] = {}
        for interface in discover_links():
            if interface.interface_index is None:
                continue
            interface_names[interface.interface_index] = interface.name
            operational_states[interface.interface_index] = (
                interface.operational_state
            )

        previous_event: InterfaceEvent | None = None
        while True:
            try:
                data = netlink.recv(65535)
            except OSError as error:
                if error.errno == errno.ENOBUFS:
                    raise InterfaceSynchronizationError(
                        errno.ENOBUFS,
                        "Netlink interface monitoring lost synchronization",
                    ) from error
                raise
            for event in _parse_messages(
                data, interface_names, operational_states
            ):
                if event == previous_event:
                    continue
                yield event
                previous_event = event


def _parse_messages(
    data: bytes,
    interface_names: dict[int, str],
    operational_states: dict[int, str],
) -> list[InterfaceEvent]:
    events: list[InterfaceEvent] = []
    offset = 0

    while offset < len(data):
        if offset + 16 > len(data):
            raise InterfaceSynchronizationError("Invalid Netlink response")
        length, message_type, flags, _, _ = struct.unpack_from(
            "=IHHII", data, offset
        )
        if length < 16 or offset + length > len(data):
            raise InterfaceSynchronizationError("Invalid Netlink response")

        payload = data[offset + 16 : offset + length]
        if message_type == _NLMSG_DONE:
            if flags & _NLM_F_DUMP_INTR:
                raise InterfaceSynchronizationError(
                    "Interrupted Netlink interface monitoring stream"
                )
            break
        if message_type == _NLMSG_ERROR:
            if len(payload) < 4:
                raise InterfaceSynchronizationError(
                    "Invalid Netlink error response"
                )
            error_code = struct.unpack_from("=i", payload)[0]
            if error_code:
                raise InterfaceSynchronizationError(
                    -error_code, "Netlink monitoring failed"
                )
        elif message_type == _NLMSG_OVERRUN:
            raise InterfaceSynchronizationError(
                "Netlink interface monitoring receive buffer overrun"
            )
        elif message_type in (_RTM_NEWLINK, _RTM_DELLINK):
            event = _parse_link_event(
                message_type,
                payload,
                interface_names,
                operational_states,
            )
            if event is not None:
                events.append(event)
        elif message_type in (_RTM_NEWADDR, _RTM_DELADDR):
            event = _parse_address_event(message_type, payload, interface_names)
            if event is not None:
                events.append(event)

        offset += _aligned(length)

    return events


def _parse_link_event(
    message_type: int,
    payload: bytes,
    interface_names: dict[int, str],
    operational_states: dict[int, str],
) -> InterfaceEvent | None:
    if len(payload) < 16:
        raise InterfaceSynchronizationError("Invalid Netlink link event")

    _, _, _, interface_index, _, changed_flags = struct.unpack_from(
        "=BBHiII", payload
    )
    attributes = _parse_attributes(payload, 16)
    name_data = attributes.get(_IFLA_IFNAME)
    interface_name = (
        name_data.rstrip(b"\0").decode(errors="replace")
        if name_data is not None
        else interface_names.get(interface_index)
    )
    if not interface_name:
        return None

    state_data = attributes.get(_IFLA_OPERSTATE)
    operational_state = (
        _OPERSTATES.get(state_data[0], "unknown") if state_data else None
    )

    if message_type == _RTM_DELLINK:
        interface_names.pop(interface_index, None)
        operational_states.pop(interface_index, None)
        return InterfaceEvent(InterfaceEventType.REMOVED, interface_name)

    previous_name = interface_names.get(interface_index)
    previous_state = operational_states.get(interface_index)
    interface_names[interface_index] = interface_name
    if operational_state is not None:
        operational_states[interface_index] = operational_state

    if previous_name is None:
        return InterfaceEvent(
            InterfaceEventType.CREATED,
            interface_name,
            operational_state=operational_state,
        )

    state_changed = (
        operational_state is not None and operational_state != previous_state
    ) or bool(changed_flags & _STATE_FLAGS)
    if state_changed:
        return InterfaceEvent(
            InterfaceEventType.STATE_CHANGED,
            interface_name,
            operational_state=operational_state or previous_state,
        )
    return None


def _parse_address_event(
    message_type: int,
    payload: bytes,
    interface_names: dict[int, str],
) -> InterfaceEvent | None:
    if len(payload) < 8:
        raise InterfaceSynchronizationError("Invalid Netlink address event")

    family, prefix_length, _, _, interface_index = struct.unpack_from(
        "=4B I", payload
    )
    if family not in (socket.AF_INET, socket.AF_INET6):
        return None

    attributes = _parse_attributes(payload, 8)
    if family == socket.AF_INET:
        packed_address = attributes.get(_IFA_LOCAL) or attributes.get(_IFA_ADDRESS)
        event_type = (
            InterfaceEventType.IPV4_ADDRESS_ADDED
            if message_type == _RTM_NEWADDR
            else InterfaceEventType.IPV4_ADDRESS_REMOVED
        )
    else:
        packed_address = attributes.get(_IFA_ADDRESS)
        event_type = (
            InterfaceEventType.IPV6_ADDRESS_ADDED
            if message_type == _RTM_NEWADDR
            else InterfaceEventType.IPV6_ADDRESS_REMOVED
        )
    if packed_address is None:
        return None

    interface_name = interface_names.get(interface_index)
    if interface_name is None:
        try:
            interface_name = socket.if_indextoname(interface_index)
        except OSError:
            return None
        interface_names[interface_index] = interface_name

    address = f"{socket.inet_ntop(family, packed_address)}/{prefix_length}"
    return InterfaceEvent(
        event_type,
        interface_name,
        address=address,
    )


def _parse_attributes(payload: bytes, offset: int) -> dict[int, bytes]:
    attributes: dict[int, bytes] = {}
    while offset + 4 <= len(payload):
        length, attribute_type = struct.unpack_from("=HH", payload, offset)
        if length < 4 or offset + length > len(payload):
            raise InterfaceSynchronizationError(
                "Invalid Netlink interface attribute"
            )
        attributes[attribute_type & 0x3FFF] = payload[offset + 4 : offset + length]
        offset += _aligned(length)
    if offset != len(payload):
        raise InterfaceSynchronizationError("Invalid Netlink interface attribute")
    return attributes


def _aligned(length: int) -> int:
    return (length + 3) & ~3
