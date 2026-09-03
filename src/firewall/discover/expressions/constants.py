_NFTA_LIST_ELEM = 1
_NFTA_EXPR_NAME = 1
_NFTA_EXPR_DATA = 2

_NFTA_META_DREG = 1
_NFTA_META_KEY = 2
_NFTA_META_SREG = 3

_NFTA_CMP_SREG = 1
_NFTA_CMP_OP = 2
_NFTA_CMP_DATA = 3

_NFTA_COUNTER_BYTES = 1
_NFTA_COUNTER_PACKETS = 2

_NFTA_IMMEDIATE_DREG = 1
_NFTA_IMMEDIATE_DATA = 2
_NFTA_DATA_VALUE = 1
_NFTA_DATA_VERDICT = 2
_NFTA_VERDICT_CODE = 1
_NFTA_VERDICT_CHAIN = 2
_NFTA_VERDICT_CHAIN_ID = 3

_NFT_REG_VERDICT = 0

_META_KEYS = {
    0: "length",
    1: "protocol",
    2: "priority",
    3: "mark",
    4: "input_interface_index",
    5: "output_interface_index",
    6: "input_interface_name",
    7: "output_interface_name",
    8: "input_interface_type",
    9: "output_interface_type",
    10: "socket_uid",
    11: "socket_gid",
    12: "nftrace",
    13: "route_class_id",
    14: "security_mark",
    15: "netfilter_protocol",
    16: "transport_protocol",
    17: "bridge_input_interface_name",
    18: "bridge_output_interface_name",
    19: "packet_type",
    20: "cpu",
    21: "input_interface_group",
    22: "output_interface_group",
    23: "cgroup",
    24: "pseudo_random",
    25: "security_path",
    26: "input_interface_kind",
    27: "output_interface_kind",
    28: "bridge_input_pvid",
    29: "bridge_input_vlan_protocol",
    30: "time_nanoseconds",
    31: "time_day",
    32: "time_hour",
    33: "slave_interface_index",
    34: "slave_interface_name",
    35: "bridge_broute",
}
_INTERFACE_STRING_KEYS = {
    "input_interface_name",
    "output_interface_name",
    "bridge_input_interface_name",
    "bridge_output_interface_name",
    "input_interface_kind",
    "output_interface_kind",
    "slave_interface_name",
}
_COMPARISON_OPERATIONS = {
    0: "equal",
    1: "not_equal",
    2: "less_than",
    3: "less_than_or_equal",
    4: "greater_than",
    5: "greater_than_or_equal",
}
_VERDICTS = {
    -1: "continue",
    -2: "break",
    -3: "jump",
    -4: "goto",
    -5: "return",
    0: "drop",
    1: "accept",
    2: "stolen",
    3: "queue",
    4: "repeat",
    5: "stop",
}
