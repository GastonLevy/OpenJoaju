from ..dto import RuleDTO
from .attributes import (
    _family_name,
    _message_attributes,
    _optional_u64,
    _required_string,
)
from .expressions import _parse_expressions


_NFTA_RULE_TABLE = 1
_NFTA_RULE_CHAIN = 2
_NFTA_RULE_HANDLE = 3
_NFTA_RULE_EXPRESSIONS = 4

def _parse_rule(payload: bytes) -> RuleDTO:
    family, attributes = _message_attributes(payload)
    table = _required_string(attributes, _NFTA_RULE_TABLE, "rule table")
    chain = _required_string(attributes, _NFTA_RULE_CHAIN, "rule chain")
    handle = _optional_u64(attributes.get(_NFTA_RULE_HANDLE))
    expressions_attribute = attributes.get(_NFTA_RULE_EXPRESSIONS)
    expressions = (
        ()
        if expressions_attribute is None
        else _parse_expressions(expressions_attribute.value)
    )
    return RuleDTO(
        family=_family_name(family),
        table=table,
        chain=chain,
        handle=handle,
        expressions=expressions,
    )
