import errno
import socket
import struct
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum

from .discover.attributes import _aligned
from .discover.chains import _parse_chain
from .discover.netlink import _NETLINK_NETFILTER, _NFNL_SUBSYS_NFTABLES
from .discover.rules import _parse_rule
from .discover.tables import _parse_table
from .dto import ChainDTO, RuleDTO, TableDTO


_NLMSG_ERROR = 2
_NLMSG_DONE = 3
_NLMSG_OVERRUN = 4
_NLM_F_DUMP_INTR = 0x10

_NFT_MSG_NEWTABLE = 0
_NFT_MSG_DELTABLE = 2
_NFT_MSG_NEWCHAIN = 3
_NFT_MSG_DELCHAIN = 5
_NFT_MSG_NEWRULE = 6
_NFT_MSG_DELRULE = 8

_NFNLGRP_NFTABLES = 7
_NFTABLES_GROUP = 1 << (_NFNLGRP_NFTABLES - 1)


class FirewallEventType(StrEnum):
    TABLE_ADDED = "table_added"
    TABLE_REMOVED = "table_removed"
    CHAIN_ADDED = "chain_added"
    CHAIN_REMOVED = "chain_removed"
    RULE_ADDED = "rule_added"
    RULE_REMOVED = "rule_removed"


@dataclass(frozen=True)
class FirewallEvent:
    event_type: FirewallEventType
    item: TableDTO | ChainDTO | RuleDTO


def monitor_events() -> Iterator[FirewallEvent]:
    """Yield nftables table, chain, and rule notifications from Netlink."""
    with socket.socket(
        socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_NETFILTER
    ) as netlink:
        netlink.bind((0, _NFTABLES_GROUP))

        while True:
            try:
                data = netlink.recv(1 << 20)
            except OSError as error:
                if error.errno == errno.ENOBUFS:
                    raise OSError(
                        errno.ENOBUFS,
                        "Nftables Netlink monitoring lost synchronization",
                    ) from error
                raise
            yield from _parse_messages(data)


def _parse_messages(data: bytes) -> Iterator[FirewallEvent]:
    offset = 0
    while offset < len(data):
        if offset + 16 > len(data):
            raise OSError("Invalid nftables Netlink event")
        length, message_type, flags, _, _ = struct.unpack_from(
            "=IHHII", data, offset
        )
        if length < 16 or offset + length > len(data):
            raise OSError("Invalid nftables Netlink event")

        payload = data[offset + 16 : offset + length]
        if message_type == _NLMSG_DONE:
            if flags & _NLM_F_DUMP_INTR:
                raise OSError("Interrupted nftables Netlink monitoring stream")
            return
        elif message_type == _NLMSG_ERROR:
            _raise_monitor_error(payload)
        elif message_type == _NLMSG_OVERRUN:
            raise OSError("Nftables Netlink monitoring receive buffer overrun")
        else:
            event = _parse_event(message_type, payload)
            if event is not None:
                yield event

        offset += _aligned(length)


def _parse_event(message_type: int, payload: bytes) -> FirewallEvent | None:
    nftables_type = message_type - (_NFNL_SUBSYS_NFTABLES << 8)
    if nftables_type == _NFT_MSG_NEWTABLE:
        return FirewallEvent(FirewallEventType.TABLE_ADDED, _parse_table(payload))
    if nftables_type == _NFT_MSG_DELTABLE:
        return FirewallEvent(FirewallEventType.TABLE_REMOVED, _parse_table(payload))
    if nftables_type == _NFT_MSG_NEWCHAIN:
        return FirewallEvent(FirewallEventType.CHAIN_ADDED, _parse_chain(payload))
    if nftables_type == _NFT_MSG_DELCHAIN:
        return FirewallEvent(FirewallEventType.CHAIN_REMOVED, _parse_chain(payload))
    if nftables_type == _NFT_MSG_NEWRULE:
        return FirewallEvent(FirewallEventType.RULE_ADDED, _parse_rule(payload))
    if nftables_type == _NFT_MSG_DELRULE:
        return FirewallEvent(FirewallEventType.RULE_REMOVED, _parse_rule(payload))
    return None


def _raise_monitor_error(payload: bytes) -> None:
    if len(payload) < 4:
        raise OSError("Invalid nftables Netlink event error response")
    error_code = struct.unpack_from("=i", payload)[0]
    if error_code:
        raise OSError(-error_code, "Nftables Netlink monitoring failed")
