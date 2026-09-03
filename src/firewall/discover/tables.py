from ..dto import TableDTO
from .attributes import _family_name, _message_attributes, _required_string


_NFTA_TABLE_NAME = 1


def _parse_table(payload: bytes) -> TableDTO:
    family, attributes = _message_attributes(payload)
    name = _required_string(attributes, _NFTA_TABLE_NAME, "table name")
    return TableDTO(family=_family_name(family), name=name)
