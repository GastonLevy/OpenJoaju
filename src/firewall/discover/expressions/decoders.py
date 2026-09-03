import struct

from ...dto import (
    ComparisonExpressionDTO,
    CounterExpressionDTO,
    ImmediateExpressionDTO,
    MetaExpressionDTO,
    VerdictExpressionDTO,
)
from ..attributes import (
    _NetlinkAttribute,
    _attribute_map,
    _optional_string,
    _optional_u32,
    _optional_u64,
    _parse_attributes,
)
from .constants import (
    _COMPARISON_OPERATIONS,
    _INTERFACE_STRING_KEYS,
    _META_KEYS,
    _NFTA_CMP_DATA,
    _NFTA_CMP_OP,
    _NFTA_CMP_SREG,
    _NFTA_COUNTER_BYTES,
    _NFTA_COUNTER_PACKETS,
    _NFTA_DATA_VALUE,
    _NFTA_DATA_VERDICT,
    _NFTA_IMMEDIATE_DATA,
    _NFTA_IMMEDIATE_DREG,
    _NFTA_META_DREG,
    _NFTA_META_KEY,
    _NFTA_META_SREG,
    _NFTA_VERDICT_CHAIN,
    _NFTA_VERDICT_CHAIN_ID,
    _NFTA_VERDICT_CODE,
    _NFT_REG_VERDICT,
    _VERDICTS,
)


def _decode_meta(
    attributes: dict[int, _NetlinkAttribute], register_context: dict[int, str]
) -> MetaExpressionDTO | None:
    key_value = _optional_u32(attributes.get(_NFTA_META_KEY))
    if key_value is None:
        return None
    key = _META_KEYS.get(key_value, f"unknown ({key_value})")
    destination_register = _optional_u32(attributes.get(_NFTA_META_DREG))
    source_register = _optional_u32(attributes.get(_NFTA_META_SREG))
    if destination_register is None and source_register is None:
        return None
    if destination_register is not None:
        register_context[destination_register] = key
    return MetaExpressionDTO(
        key=key,
        destination_register=destination_register,
        source_register=source_register,
    )


def _decode_comparison(
    attributes: dict[int, _NetlinkAttribute], register_context: dict[int, str]
) -> ComparisonExpressionDTO | None:
    source_register = _optional_u32(attributes.get(_NFTA_CMP_SREG))
    operation_value = _optional_u32(attributes.get(_NFTA_CMP_OP))
    data_attribute = attributes.get(_NFTA_CMP_DATA)
    if source_register is None or operation_value is None or data_attribute is None:
        return None
    data_attributes = _attribute_map(_parse_attributes(data_attribute.value))
    value_attribute = data_attributes.get(_NFTA_DATA_VALUE)
    if value_attribute is None:
        return None

    operation = _COMPARISON_OPERATIONS.get(
        operation_value, f"unknown ({operation_value})"
    )
    data: bytes | str = value_attribute.value
    data_type = "bytes"
    if register_context.get(source_register) in _INTERFACE_STRING_KEYS:
        decoded = _decode_interface_string(value_attribute.value)
        if decoded is not None:
            data = decoded
            data_type = "interface_name"
    return ComparisonExpressionDTO(
        source_register=source_register,
        operation=operation,
        data=data,
        data_type=data_type,
    )


def _decode_counter(
    attributes: dict[int, _NetlinkAttribute],
) -> CounterExpressionDTO | None:
    byte_count = _optional_u64(attributes.get(_NFTA_COUNTER_BYTES))
    packet_count = _optional_u64(attributes.get(_NFTA_COUNTER_PACKETS))
    if byte_count is None or packet_count is None:
        return None
    return CounterExpressionDTO(packets=packet_count, bytes=byte_count)


def _decode_immediate(
    attributes: dict[int, _NetlinkAttribute], register_context: dict[int, str]
) -> ImmediateExpressionDTO | VerdictExpressionDTO | None:
    destination_register = _optional_u32(attributes.get(_NFTA_IMMEDIATE_DREG))
    data_attribute = attributes.get(_NFTA_IMMEDIATE_DATA)
    if destination_register is None or data_attribute is None:
        return None
    data_attributes = _attribute_map(_parse_attributes(data_attribute.value))
    verdict_attribute = data_attributes.get(_NFTA_DATA_VERDICT)
    if destination_register == _NFT_REG_VERDICT and verdict_attribute is not None:
        return _decode_verdict(verdict_attribute)
    value_attribute = data_attributes.get(_NFTA_DATA_VALUE)
    if value_attribute is None:
        return None
    register_context.pop(destination_register, None)
    return ImmediateExpressionDTO(
        destination_register=destination_register,
        data=value_attribute.value,
    )


def _decode_verdict(
    verdict_attribute: _NetlinkAttribute,
) -> VerdictExpressionDTO | None:
    attributes = _attribute_map(_parse_attributes(verdict_attribute.value))
    code_attribute = attributes.get(_NFTA_VERDICT_CODE)
    if code_attribute is None:
        return None
    if len(code_attribute.value) != 4:
        raise OSError("Invalid nftables signed 32-bit attribute")
    code = struct.unpack("!i", code_attribute.value)[0]
    action = _VERDICTS.get(code, f"unknown ({code})")
    return VerdictExpressionDTO(
        action=action,
        chain=_optional_string(attributes.get(_NFTA_VERDICT_CHAIN)),
        chain_id=_optional_u32(attributes.get(_NFTA_VERDICT_CHAIN_ID)),
    )


def _decode_interface_string(value: bytes) -> str | None:
    try:
        return value.rstrip(b"\0").decode("utf-8")
    except UnicodeDecodeError:
        return None
