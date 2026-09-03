from ...dto import ExpressionDTO, RuleExpressionDTO
from ..attributes import (
    _NetlinkAttribute,
    _attribute_map,
    _generic_attributes,
    _parse_attributes,
    _required_string,
)
from .constants import _NFTA_EXPR_DATA, _NFTA_EXPR_NAME, _NFTA_LIST_ELEM
from .decoders import (
    _decode_comparison,
    _decode_counter,
    _decode_immediate,
    _decode_meta,
)


def _parse_expressions(payload: bytes) -> tuple[RuleExpressionDTO, ...]:
    expressions: list[RuleExpressionDTO] = []
    register_context: dict[int, str] = {}

    for element in _parse_attributes(payload):
        if element.attribute_type != _NFTA_LIST_ELEM:
            continue
        attributes = _attribute_map(_parse_attributes(element.value))
        name = _required_string(attributes, _NFTA_EXPR_NAME, "expression name")
        data = attributes.get(_NFTA_EXPR_DATA)
        expression = _decode_expression(name, data, register_context)
        if expression is None:
            generic_attributes = () if data is None else _generic_attributes(data.value)
            expression = ExpressionDTO(name=name, attributes=generic_attributes)
            register_context.clear()
        expressions.append(expression)

    return tuple(expressions)


def _decode_expression(
    name: str,
    data: _NetlinkAttribute | None,
    register_context: dict[int, str],
) -> RuleExpressionDTO | None:
    if data is None:
        return None
    attributes = _attribute_map(_parse_attributes(data.value))
    if name == "meta":
        return _decode_meta(attributes, register_context)
    if name == "cmp":
        return _decode_comparison(attributes, register_context)
    if name == "counter":
        return _decode_counter(attributes)
    if name == "immediate":
        return _decode_immediate(attributes, register_context)
    return None
