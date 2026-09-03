import ipaddress
import socket
import struct

from ..dto import RouteDTO


_NETLINK_ROUTE = 0
_NLMSG_ERROR = 2
_NLMSG_DONE = 3
_RTM_NEWROUTE = 24
_RTM_GETROUTE = 26
_NLM_F_REQUEST = 1
_NLM_F_DUMP = 0x300

_RTA_DST = 1
_RTA_OIF = 4
_RTA_GATEWAY = 5
_RTA_PRIORITY = 6
_RTA_PREFSRC = 7
_RTA_MULTIPATH = 9
_RTA_TABLE = 15
_RTA_VIA = 18

_TABLE_NAMES = {
    253: "default",
    254: "main",
    255: "local",
}

_PROTOCOL_NAMES = {
    0: "unspecified",
    1: "redirect",
    2: "kernel",
    3: "boot",
    4: "static",
    8: "gated",
    9: "router advertisement",
    10: "mrt",
    11: "zebra",
    12: "bird",
    13: "dnrouter",
    14: "xorp",
    15: "ntkernel",
    16: "dhcp",
    17: "mrouted",
    18: "keepalived",
    42: "babel",
    186: "bgp",
    187: "isis",
    188: "ospf",
    189: "rip",
    192: "eigrp",
}
_SCOPE_NAMES = {
    0: "global",
    200: "site",
    253: "link",
    254: "host",
    255: "nowhere",
}
_TYPE_NAMES = {
    0: "unspecified",
    1: "unicast",
    2: "local",
    3: "broadcast",
    4: "anycast",
    5: "multicast",
    6: "blackhole",
    7: "unreachable",
    8: "prohibit",
    9: "throw",
    10: "nat",
    11: "xresolve",
}


def discover_routes() -> list[RouteDTO]:
    routes: list[RouteDTO] = []

    with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_ROUTE) as netlink:
        netlink.bind((0, 0))
        sequence = 1
        request = struct.pack(
            "=IHHII8BI",
            28,
            _RTM_GETROUTE,
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
            0,
            0,
        )
        netlink.send(request)

        finished = False
        while not finished:
            data = netlink.recv(65535)
            offset = 0

            while offset + 16 <= len(data):
                length, message_type, _, message_sequence, _ = struct.unpack_from(
                    "=IHHII", data, offset
                )
                if length < 16 or offset + length > len(data):
                    raise OSError("Invalid Netlink route response")
                if message_sequence != sequence:
                    offset += _aligned(length)
                    continue
                if message_type == _NLMSG_DONE:
                    finished = True
                    break
                if message_type == _NLMSG_ERROR:
                    if length < 20:
                        raise OSError("Invalid Netlink route error response")
                    error_code = struct.unpack_from("=i", data, offset + 16)[0]
                    if error_code:
                        raise OSError(-error_code, "Netlink route discovery failed")
                    finished = True
                    break
                if message_type == _RTM_NEWROUTE:
                    routes.extend(_parse_route(data[offset + 16 : offset + length]))

                offset += _aligned(length)

    return routes


def _parse_route(payload: bytes) -> list[RouteDTO]:
    if len(payload) < 12:
        raise OSError("Invalid Netlink route payload")

    family, prefix_length, _, _, table_id, protocol, scope, route_type, _ = (
        struct.unpack_from("=8BI", payload)
    )
    if family not in (socket.AF_INET, socket.AF_INET6):
        return []

    attributes = _parse_attributes(payload, 12)
    extended_table_id = _uint32(attributes.get(_RTA_TABLE))
    if extended_table_id is not None:
        table_id = extended_table_id
    route_values = {
        "destination": _destination(family, prefix_length, attributes.get(_RTA_DST)),
        "preferred_source": _address(attributes.get(_RTA_PREFSRC), family),
        "metric": _uint32(attributes.get(_RTA_PRIORITY)),
        "protocol": _name(_PROTOCOL_NAMES, protocol),
        "scope": _name(_SCOPE_NAMES, scope),
        "route_type": _name(_TYPE_NAMES, route_type),
        "family": "ipv4" if family == socket.AF_INET else "ipv6",
        "table": _TABLE_NAMES.get(table_id, str(table_id)),
    }

    multipath = attributes.get(_RTA_MULTIPATH)
    if multipath is not None:
        return [
            RouteDTO(gateway=gateway, interface=interface, **route_values)
            for gateway, interface in _parse_multipath(multipath, family)
        ]

    return [
        RouteDTO(
            gateway=_gateway(attributes, family),
            interface=_interface_name(_uint32(attributes.get(_RTA_OIF))),
            **route_values,
        )
    ]


def _parse_attributes(payload: bytes, offset: int = 0) -> dict[int, bytes]:
    attributes: dict[int, bytes] = {}
    while offset + 4 <= len(payload):
        length, attribute_type = struct.unpack_from("=HH", payload, offset)
        if length < 4 or offset + length > len(payload):
            raise OSError("Invalid Netlink route attribute")
        attributes[attribute_type & 0x3FFF] = payload[offset + 4 : offset + length]
        offset += _aligned(length)
    return attributes


def _parse_multipath(payload: bytes, family: int) -> list[tuple[str | None, str | None]]:
    next_hops: list[tuple[str | None, str | None]] = []
    offset = 0
    while offset + 8 <= len(payload):
        length, _, _, interface_index = struct.unpack_from("=HBBi", payload, offset)
        if length < 8 or offset + length > len(payload):
            raise OSError("Invalid Netlink multipath route")
        attributes = _parse_attributes(payload[offset : offset + length], 8)
        next_hops.append(
            (_gateway(attributes, family), _interface_name(interface_index))
        )
        offset += _aligned(length)
    return next_hops


def _destination(family: int, prefix_length: int, value: bytes | None) -> str:
    if value is None:
        address = "0.0.0.0" if family == socket.AF_INET else "::"
    else:
        address = socket.inet_ntop(family, value)
    return str(ipaddress.ip_network(f"{address}/{prefix_length}", strict=False))


def _gateway(attributes: dict[int, bytes], family: int) -> str | None:
    value = attributes.get(_RTA_GATEWAY)
    if value is not None:
        return _address(value, family)

    via = attributes.get(_RTA_VIA)
    if via is None or len(via) < 2:
        return None
    via_family = struct.unpack_from("=H", via)[0]
    if via_family not in (socket.AF_INET, socket.AF_INET6):
        return None
    return socket.inet_ntop(via_family, via[2:])


def _address(value: bytes | None, family: int) -> str | None:
    if value is None:
        return None
    return socket.inet_ntop(family, value)


def _uint32(value: bytes | None) -> int | None:
    if value is None:
        return None
    if len(value) < 4:
        raise OSError("Invalid Netlink integer attribute")
    return struct.unpack_from("=I", value)[0]


def _interface_name(interface_index: int | None) -> str | None:
    if interface_index is None or interface_index == 0:
        return None
    try:
        return socket.if_indextoname(interface_index)
    except OSError:
        return None


def _name(names: dict[int, str], value: int) -> str:
    return names.get(value, f"unknown ({value})")


def _aligned(length: int) -> int:
    return (length + 3) & ~3
