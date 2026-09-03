from ..dto import ChainDTO
from .attributes import (
    _attribute_map,
    _family_name,
    _message_attributes,
    _optional_i32,
    _optional_string,
    _optional_u32,
    _parse_attributes,
    _required_string,
)


_NFTA_CHAIN_TABLE = 1
_NFTA_CHAIN_NAME = 3
_NFTA_CHAIN_HOOK = 4
_NFTA_CHAIN_POLICY = 5
_NFTA_CHAIN_TYPE = 7

_NFTA_HOOK_HOOKNUM = 1
_NFTA_HOOK_PRIORITY = 2

_INET_HOOK_NAMES = {
    0: "prerouting",
    1: "input",
    2: "forward",
    3: "output",
    4: "postrouting",
    5: "ingress",
}
_ARP_HOOK_NAMES = {0: "input", 1: "output", 2: "forward"}
_BRIDGE_HOOK_NAMES = {
    0: "prerouting",
    1: "input",
    2: "forward",
    3: "output",
    4: "postrouting",
    5: "broute",
}
_NETDEV_HOOK_NAMES = {0: "ingress", 1: "egress"}
_POLICY_NAMES = {0: "drop", 1: "accept"}


def _parse_chain(payload: bytes) -> ChainDTO:
    family, attributes = _message_attributes(payload)
    table = _required_string(attributes, _NFTA_CHAIN_TABLE, "chain table")
    name = _required_string(attributes, _NFTA_CHAIN_NAME, "chain name")
    chain_type = _optional_string(attributes.get(_NFTA_CHAIN_TYPE))
    policy_value = _optional_u32(attributes.get(_NFTA_CHAIN_POLICY))
    policy = (
        None
        if policy_value is None
        else _POLICY_NAMES.get(policy_value, f"unknown ({policy_value})")
    )

    hook = None
    priority = None
    hook_attribute = attributes.get(_NFTA_CHAIN_HOOK)
    if hook_attribute is not None:
        hook_attributes = _attribute_map(_parse_attributes(hook_attribute.value))
        hook_number = _optional_u32(hook_attributes.get(_NFTA_HOOK_HOOKNUM))
        if hook_number is not None:
            hook = _hook_name(family, hook_number)
        priority = _optional_i32(hook_attributes.get(_NFTA_HOOK_PRIORITY))

    return ChainDTO(
        family=_family_name(family),
        table=table,
        name=name,
        hook=hook,
        priority=priority,
        policy=policy,
        chain_type=chain_type,
    )


def _hook_name(family: int, hook: int) -> str:
    if family == 3:
        names = _ARP_HOOK_NAMES
    elif family == 5:
        names = _NETDEV_HOOK_NAMES
    elif family == 7:
        names = _BRIDGE_HOOK_NAMES
    else:
        names = _INET_HOOK_NAMES
    return names.get(hook, f"unknown ({hook})")
