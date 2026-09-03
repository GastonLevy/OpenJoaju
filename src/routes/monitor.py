import errno
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
_NLMSG_OVERRUN = 4
_NLM_F_DUMP_INTR = 0x10
_RTM_NEWROUTE = 24
_RTM_DELROUTE = 25
_RTMGRP_IPV4_ROUTE = 0x40
_RTMGRP_IPV6_ROUTE = 0x400


class RouteEventType(StrEnum):
    ADDED = "route_added"
    REMOVED = "route_removed"


class RouteSynchronizationError(OSError):
    pass


@dataclass(frozen=True)
class RouteEvent:
    event_type: RouteEventType
    route: RouteDTO


def monitor_events() -> Iterator[RouteEvent]:
    groups = _RTMGRP_IPV4_ROUTE | _RTMGRP_IPV6_ROUTE

    with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_ROUTE) as netlink:
        netlink.bind((0, groups))

        while True:
            try:
                data = netlink.recv(65535)
            except OSError as error:
                if error.errno == errno.ENOBUFS:
                    raise RouteSynchronizationError(
                        errno.ENOBUFS,
                        "Netlink route monitoring lost synchronization",
                    ) from error
                raise
            yield from _parse_messages(data)


def _parse_messages(data: bytes) -> Iterator[RouteEvent]:
    offset = 0

    while offset < len(data):
        if offset + 16 > len(data):
            raise RouteSynchronizationError("Invalid Netlink route event")
        length, message_type, flags, _, _ = struct.unpack_from(
            "=IHHII", data, offset
        )
        if length < 16 or offset + length > len(data):
            raise RouteSynchronizationError("Invalid Netlink route event")

        if message_type == _NLMSG_DONE:
            if flags & _NLM_F_DUMP_INTR:
                raise RouteSynchronizationError(
                    "Interrupted Netlink route monitoring stream"
                )
            return

        if message_type == _NLMSG_ERROR:
            if length < 20:
                raise RouteSynchronizationError(
                    "Invalid Netlink route event error response"
                )
            error_code = struct.unpack_from("=i", data, offset + 16)[0]
            if error_code:
                raise RouteSynchronizationError(
                    -error_code, "Netlink route monitoring failed"
                )
        elif message_type == _NLMSG_OVERRUN:
            raise RouteSynchronizationError(
                "Netlink route monitoring receive buffer overrun"
            )
        elif message_type in (_RTM_NEWROUTE, _RTM_DELROUTE):
            event_type = (
                RouteEventType.ADDED
                if message_type == _RTM_NEWROUTE
                else RouteEventType.REMOVED
            )
            payload = data[offset + 16 : offset + length]
            try:
                routes = _parse_route(payload)
            except OSError as error:
                raise RouteSynchronizationError(
                    "Invalid Netlink route event payload"
                ) from error
            for route in routes:
                yield RouteEvent(event_type=event_type, route=route)

        offset += _aligned(length)
