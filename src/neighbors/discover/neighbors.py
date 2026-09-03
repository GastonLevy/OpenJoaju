import socket
import struct

from ..dto import NeighborDTO


_NETLINK_ROUTE = 0
_NLMSG_ERROR = 2
_NLMSG_DONE = 3
_RTM_NEWNEIGH = 28
_RTM_GETNEIGH = 30
_NLM_F_REQUEST = 1
_NLM_F_DUMP = 0x300

_NDA_DST = 1
_NDA_LLADDR = 2

_STATE_NAMES = {
    0x00: "none",
    0x01: "incomplete",
    0x02: "reachable",
    0x04: "stale",
    0x08: "delay",
    0x10: "probe",
    0x20: "failed",
    0x40: "noarp",
    0x80: "permanent",
}


def discover_neighbors() -> list[NeighborDTO]:
    neighbors: list[NeighborDTO] = []

    with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_ROUTE) as netlink:
        netlink.bind((0, 0))
        sequence = 1
        request = struct.pack(
            "=IHHIIBBHiHBB",
            28,
            _RTM_GETNEIGH,
            _NLM_F_REQUEST | _NLM_F_DUMP,
            sequence,
            0,
            socket.AF_UNSPEC,
            0,
            0,
            0,
            0,
            0,
            0,
        )
        netlink.send(request)

        finished = False
        while not finished:
            data = netlink.recv(65535)
            offset = 0

            while offset < len(data):
                if offset + 16 > len(data):
                    raise OSError("Invalid Netlink neighbor response")
                length, message_type, _, message_sequence, _ = struct.unpack_from(
                    "=IHHII", data, offset
                )
                if length < 16 or offset + length > len(data):
                    raise OSError("Invalid Netlink neighbor response")
                if message_sequence != sequence:
                    offset += _aligned(length)
                    continue
                if message_type == _NLMSG_DONE:
                    finished = True
                    break
                if message_type == _NLMSG_ERROR:
                    if length < 20:
                        raise OSError("Invalid Netlink neighbor error response")
                    error_code = struct.unpack_from("=i", data, offset + 16)[0]
                    if error_code:
                        raise OSError(-error_code, "Netlink neighbor discovery failed")
                    finished = True
                    break
                if message_type == _RTM_NEWNEIGH:
                    neighbor = _parse_neighbor(data[offset + 16 : offset + length])
                    if neighbor is not None:
                        neighbors.append(neighbor)

                offset += _aligned(length)

    return neighbors


def _parse_neighbor(payload: bytes) -> NeighborDTO | None:
    if len(payload) < 12:
        raise OSError("Invalid Netlink neighbor payload")

    family, _, _, interface_index, state, _, _ = struct.unpack_from(
        "=BBHiHBB", payload
    )
    if family not in (socket.AF_INET, socket.AF_INET6):
        return None

    attributes = _parse_attributes(payload, 12)
    destination = attributes.get(_NDA_DST)
    if destination is None:
        return None

    expected_length = 4 if family == socket.AF_INET else 16
    if len(destination) != expected_length:
        raise OSError("Invalid Netlink neighbor address")

    link_layer_address = attributes.get(_NDA_LLADDR)
    try:
        interface = socket.if_indextoname(interface_index)
    except OSError:
        interface = None

    return NeighborDTO(
        ip_address=socket.inet_ntop(family, destination),
        mac_address=_format_link_layer_address(link_layer_address),
        interface=interface,
        interface_index=interface_index,
        family="ipv4" if family == socket.AF_INET else "ipv6",
        state=_normalize_state(state),
    )


def _parse_attributes(payload: bytes, offset: int = 0) -> dict[int, bytes]:
    attributes: dict[int, bytes] = {}
    while offset + 4 <= len(payload):
        length, attribute_type = struct.unpack_from("=HH", payload, offset)
        if length < 4 or offset + length > len(payload):
            raise OSError("Invalid Netlink neighbor attribute")
        attributes[attribute_type & 0x3FFF] = payload[offset + 4 : offset + length]
        offset += _aligned(length)
    return attributes


def _format_link_layer_address(value: bytes | None) -> str | None:
    if not value:
        return None
    return ":".join(f"{octet:02x}" for octet in value)


def _normalize_state(value: int) -> str:
    return _STATE_NAMES.get(value, f"unknown:0x{value:02x}")


def _aligned(length: int) -> int:
    return (length + 3) & ~3
