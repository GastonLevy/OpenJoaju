import struct
from dataclasses import dataclass

from ..dto import ExpressionAttributeDTO


_NLA_F_NESTED = 1 << 15
_NLA_F_NET_BYTEORDER = 1 << 14
_NLA_TYPE_MASK = 0x3FFF

_FAMILY_NAMES = {
    0: "unspecified",
    1: "inet",
    2: "ip",
    3: "arp",
    5: "netdev",
    7: "bridge",
    10: "ip6",
    12: "decnet",
}


@dataclass(frozen=True)
class _NetlinkAttribute:
    attribute_type: int
    nested: bool
    network_byte_order: bool
    value: bytes


def _message_attributes(payload: bytes) -> tuple[int, dict[int, _NetlinkAttribute]]:
    if len(payload) < 4:
        raise OSError("Invalid nftables message payload")
    family = payload[0]
    return family, _attribute_map(_parse_attributes(payload, 4))


def _parse_attributes(payload: bytes, offset: int = 0) -> list[_NetlinkAttribute]:
    attributes: list[_NetlinkAttribute] = []
    while offset < len(payload):
        if offset + 4 > len(payload):
            raise OSError("Invalid nftables Netlink attribute header")
        length, raw_type = struct.unpack_from("=HH", payload, offset)
        if length < 4 or offset + length > len(payload):
            raise OSError("Invalid nftables Netlink attribute")
        attributes.append(
            _NetlinkAttribute(
                attribute_type=raw_type & _NLA_TYPE_MASK,
                nested=bool(raw_type & _NLA_F_NESTED),
                network_byte_order=bool(raw_type & _NLA_F_NET_BYTEORDER),
                value=payload[offset + 4 : offset + length],
            )
        )
        offset += _aligned(length)
    return attributes


def _attribute_map(
    attributes: list[_NetlinkAttribute],
) -> dict[int, _NetlinkAttribute]:
    return {attribute.attribute_type: attribute for attribute in attributes}


def _required_string(
    attributes: dict[int, _NetlinkAttribute], attribute_type: int, description: str
) -> str:
    value = _optional_string(attributes.get(attribute_type))
    if value is None:
        raise OSError(f"Missing nftables {description}")
    return value


def _optional_string(attribute: _NetlinkAttribute | None) -> str | None:
    if attribute is None:
        return None
    return attribute.value.rstrip(b"\0").decode(errors="replace")


def _optional_u32(attribute: _NetlinkAttribute | None) -> int | None:
    if attribute is None:
        return None
    if len(attribute.value) != 4:
        raise OSError("Invalid nftables 32-bit attribute")
    return struct.unpack("!I", attribute.value)[0]


def _optional_i32(attribute: _NetlinkAttribute | None) -> int | None:
    if attribute is None:
        return None
    if len(attribute.value) != 4:
        raise OSError("Invalid nftables signed 32-bit attribute")
    return struct.unpack("!i", attribute.value)[0]


def _optional_u64(attribute: _NetlinkAttribute | None) -> int | None:
    if attribute is None:
        return None
    if len(attribute.value) != 8:
        raise OSError("Invalid nftables 64-bit attribute")
    return struct.unpack("!Q", attribute.value)[0]


def _generic_attributes(payload: bytes) -> tuple[ExpressionAttributeDTO, ...]:
    result: list[ExpressionAttributeDTO] = []
    for attribute in _parse_attributes(payload):
        value: bytes | tuple[ExpressionAttributeDTO, ...]
        if attribute.nested:
            value = _generic_attributes(attribute.value)
        else:
            value = attribute.value
        result.append(
            ExpressionAttributeDTO(
                attribute_type=attribute.attribute_type,
                nested=attribute.nested,
                network_byte_order=attribute.network_byte_order,
                value=value,
            )
        )
    return tuple(result)


def _family_name(family: int) -> str:
    return _FAMILY_NAMES.get(family, f"unknown ({family})")


def _aligned(length: int) -> int:
    return (length + 3) & ~3
