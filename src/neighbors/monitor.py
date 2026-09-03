import errno
import socket
import struct
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum

from .discover.neighbors import _aligned, _parse_neighbor
from .dto import NeighborDTO


_NETLINK_ROUTE = 0
_NLMSG_ERROR = 2
_NLMSG_DONE = 3
_NLMSG_OVERRUN = 4
_NLM_F_DUMP_INTR = 0x10
_RTM_NEWNEIGH = 28
_RTM_DELNEIGH = 29
_RTMGRP_NEIGH = 0x4


class NeighborEventType(StrEnum):
    UPSERTED = "neighbor_upserted"
    REMOVED = "neighbor_removed"


class NeighborSynchronizationError(OSError):
    pass


@dataclass(frozen=True)
class NeighborEvent:
    event_type: NeighborEventType
    neighbor: NeighborDTO


def monitor_events() -> Iterator[NeighborEvent]:
    with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_ROUTE) as netlink:
        netlink.bind((0, _RTMGRP_NEIGH))

        while True:
            try:
                data = netlink.recv(65535)
            except OSError as error:
                if error.errno == errno.ENOBUFS:
                    raise NeighborSynchronizationError(
                        errno.ENOBUFS,
                        "Netlink neighbor monitoring lost synchronization",
                    ) from error
                raise
            yield from _parse_messages(data)


def _parse_messages(data: bytes) -> Iterator[NeighborEvent]:
    offset = 0

    while offset < len(data):
        if offset + 16 > len(data):
            raise NeighborSynchronizationError("Invalid Netlink neighbor event")
        length, message_type, flags, _, _ = struct.unpack_from(
            "=IHHII", data, offset
        )
        if length < 16 or offset + length > len(data):
            raise NeighborSynchronizationError("Invalid Netlink neighbor event")

        if message_type == _NLMSG_DONE:
            if flags & _NLM_F_DUMP_INTR:
                raise NeighborSynchronizationError(
                    "Interrupted Netlink neighbor monitoring stream"
                )
            return

        if message_type == _NLMSG_ERROR:
            if length < 20:
                raise NeighborSynchronizationError(
                    "Invalid Netlink neighbor event error response"
                )
            error_code = struct.unpack_from("=i", data, offset + 16)[0]
            if error_code:
                raise NeighborSynchronizationError(
                    -error_code, "Netlink neighbor monitoring failed"
                )
        elif message_type == _NLMSG_OVERRUN:
            raise NeighborSynchronizationError(
                "Netlink neighbor monitoring receive buffer overrun"
            )
        elif message_type in (_RTM_NEWNEIGH, _RTM_DELNEIGH):
            payload = data[offset + 16 : offset + length]
            try:
                neighbor = _parse_neighbor(payload)
            except OSError as error:
                raise NeighborSynchronizationError(
                    "Invalid Netlink neighbor event payload"
                ) from error
            if neighbor is not None:
                event_type = (
                    NeighborEventType.UPSERTED
                    if message_type == _RTM_NEWNEIGH
                    else NeighborEventType.REMOVED
                )
                yield NeighborEvent(event_type=event_type, neighbor=neighbor)

        offset += _aligned(length)
