import socket
import struct


_NETLINK_ROUTE = 0
_NLMSG_DONE = 3
_NLMSG_ERROR = 2
_RTM_NEWADDR = 20
_RTM_GETADDR = 22
_NLM_F_REQUEST = 1
_NLM_F_DUMP = 0x300
_IFA_ADDRESS = 1
_IFA_LOCAL = 2


def discover_addresses() -> dict[str, tuple[list[str], list[str]]]:
    addresses: dict[str, tuple[list[str], list[str]]] = {}

    with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_ROUTE) as netlink:
        netlink.bind((0, 0))
        sequence = 1
        message = struct.pack(
            "=IHHII4B I",
            24,
            _RTM_GETADDR,
            _NLM_F_REQUEST | _NLM_F_DUMP,
            sequence,
            0,
            socket.AF_UNSPEC,
            0,
            0,
            0,
            0,
        )
        netlink.send(message)

        finished = False
        while not finished:
            data = netlink.recv(65535)
            offset = 0

            while offset + 16 <= len(data):
                length, message_type, _, message_sequence, _ = struct.unpack_from(
                    "=IHHII", data, offset
                )
                if length < 16:
                    raise OSError("Invalid netlink response")
                if message_sequence != sequence:
                    offset += _aligned(length)
                    continue
                if message_type == _NLMSG_DONE:
                    finished = True
                    break
                if message_type == _NLMSG_ERROR:
                    error_code = struct.unpack_from("=i", data, offset + 16)[0]
                    if error_code:
                        raise OSError(-error_code, "Netlink address discovery failed")
                    finished = True
                    break
                if message_type == _RTM_NEWADDR:
                    _add_address(data[offset + 16 : offset + length], addresses)

                offset += _aligned(length)

    return addresses


def _add_address(
    payload: bytes, addresses: dict[str, tuple[list[str], list[str]]]
) -> None:
    family, prefix_length, _, _, interface_index = struct.unpack_from(
        "=4B I", payload
    )
    attributes: dict[int, bytes] = {}
    offset = 8

    while offset + 4 <= len(payload):
        length, attribute_type = struct.unpack_from("=HH", payload, offset)
        if length < 4:
            break
        attributes[attribute_type] = payload[offset + 4 : offset + length]
        offset += _aligned(length)

    if family == socket.AF_INET:
        packed_address = attributes.get(_IFA_LOCAL) or attributes.get(_IFA_ADDRESS)
    elif family == socket.AF_INET6:
        packed_address = attributes.get(_IFA_ADDRESS)
    else:
        return

    if packed_address is None:
        return

    try:
        interface_name = socket.if_indextoname(interface_index)
    except OSError:
        return

    ipv4_addresses, ipv6_addresses = addresses.setdefault(interface_name, ([], []))
    address = f"{socket.inet_ntop(family, packed_address)}/{prefix_length}"
    target = ipv4_addresses if family == socket.AF_INET else ipv6_addresses
    if address not in target:
        target.append(address)


def _aligned(length: int) -> int:
    return (length + 3) & ~3
