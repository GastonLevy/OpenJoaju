import errno
import socket
import struct

from ..dto import ChainDTO, RuleDTO, TableDTO
from .attributes import _aligned
from .chains import _parse_chain
from .rules import _parse_rule
from .tables import _parse_table


_NETLINK_NETFILTER = 12
_NLMSG_ERROR = 2
_NLMSG_DONE = 3
_NLMSG_OVERRUN = 4
_NLM_F_REQUEST = 1
_NLM_F_DUMP = 0x300
_NLM_F_DUMP_INTR = 0x10
_NFNL_SUBSYS_NFTABLES = 10

_NFT_MSG_NEWTABLE = 0
_NFT_MSG_GETTABLE = 1
_NFT_MSG_NEWCHAIN = 3
_NFT_MSG_GETCHAIN = 4
_NFT_MSG_NEWRULE = 6
_NFT_MSG_GETRULE = 7


def discover_firewall() -> tuple[
    list[TableDTO],
    list[ChainDTO],
    list[RuleDTO],
]:
    with socket.socket(
        socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_NETFILTER
    ) as netlink:
        netlink.bind((0, 0))
        tables = [
            _parse_table(payload)
            for payload in _dump(
                netlink, _NFT_MSG_GETTABLE, _NFT_MSG_NEWTABLE, sequence=1
            )
        ]
        chains = [
            _parse_chain(payload)
            for payload in _dump(
                netlink, _NFT_MSG_GETCHAIN, _NFT_MSG_NEWCHAIN, sequence=2
            )
        ]
        rules = [
            _parse_rule(payload)
            for payload in _dump(
                netlink, _NFT_MSG_GETRULE, _NFT_MSG_NEWRULE, sequence=3
            )
        ]

    return tables, chains, rules


def _dump(
    netlink: socket.socket,
    request_type: int,
    response_type: int,
    *,
    sequence: int,
) -> list[bytes]:
    message_type = (_NFNL_SUBSYS_NFTABLES << 8) | request_type
    expected_type = (_NFNL_SUBSYS_NFTABLES << 8) | response_type
    payload = struct.pack("!BBH", 0, 0, 0)
    request = struct.pack(
        "=IHHII",
        16 + len(payload),
        message_type,
        _NLM_F_REQUEST | _NLM_F_DUMP,
        sequence,
        0,
    ) + payload
    netlink.send(request)

    messages: list[bytes] = []
    finished = False
    while not finished:
        data = netlink.recv(1 << 20)
        offset = 0
        while offset + 16 <= len(data):
            length, current_type, flags, current_sequence, _ = struct.unpack_from(
                "=IHHII", data, offset
            )
            if length < 16 or offset + length > len(data):
                raise OSError("Invalid nftables Netlink response")
            if current_sequence != sequence:
                offset += _aligned(length)
                continue
            if current_type == _NLMSG_DONE:
                if flags & _NLM_F_DUMP_INTR:
                    raise OSError("Interrupted nftables Netlink dump")
                finished = True
                break
            if current_type == _NLMSG_ERROR:
                _raise_netlink_error(data[offset + 16 : offset + length])
                finished = True
                break
            if current_type == _NLMSG_OVERRUN:
                raise OSError("Nftables Netlink receive buffer overrun")
            if current_type == expected_type:
                messages.append(data[offset + 16 : offset + length])
            offset += _aligned(length)
    return messages


def _raise_netlink_error(payload: bytes) -> None:
    if len(payload) < 4:
        raise OSError("Invalid nftables Netlink error response")
    error_code = struct.unpack_from("=i", payload)[0]
    if error_code == 0:
        return
    error_number = -error_code
    if error_number in (errno.EACCES, errno.EPERM):
        raise PermissionError(
            error_number,
            "nftables inspection requires appropriate privileges",
        )
    raise OSError(error_number, "Nftables Netlink discovery failed")
