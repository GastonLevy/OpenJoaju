import socket
import struct
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum

from .discover.routes import _aligned, _parse_route
from .dto import RouteDTO


_NETLINK_ROUTE = 0
_NLMSG_ERROR = 2
_NLMSG_DONE = 3
_RTM_NEWROUTE = 24
_RTM_DELROUTE = 25
_RTMGRP_IPV4_ROUTE = 0x40
_RTMGRP_IPV6_ROUTE = 0x400


class RouteEventType(StrEnum):
    ADDED = "route_added"
    REMOVED = "route_removed"


@dataclass(frozen=True)
class RouteEvent:
    event_type: RouteEventType
    route: RouteDTO


def monitor_events() -> Iterator[RouteEvent]:
    groups = _RTMGRP_IPV4_ROUTE | _RTMGRP_IPV6_ROUTE

    with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_ROUTE) as netlink:
        netlink.bind((0, groups))

        while True:
            yield from _parse_messages(netlink.recv(65535))


def _parse_messages(data: bytes) -> Iterator[RouteEvent]:
    offset = 0

    while offset + 16 <= len(data):
        length, message_type, _, _, _ = struct.unpack_from("=IHHII", data, offset)
        if length < 16 or offset + length > len(data):
            raise OSError("Invalid Netlink route event")

        if message_type == _NLMSG_DONE:
            return

        if message_type == _NLMSG_ERROR:
            if length < 20:
                raise OSError("Invalid Netlink route event error response")
            error_code = struct.unpack_from("=i", data, offset + 16)[0]
            if error_code:
                raise OSError(-error_code, "Netlink route monitoring failed")
        elif message_type in (_RTM_NEWROUTE, _RTM_DELROUTE):
            event_type = (
                RouteEventType.ADDED
                if message_type == _RTM_NEWROUTE
                else RouteEventType.REMOVED
            )
            payload = data[offset + 16 : offset + length]
            for route in _parse_route(payload):
                yield RouteEvent(event_type=event_type, route=route)

        offset += _aligned(length)
