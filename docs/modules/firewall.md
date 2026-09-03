# Firewall

Path: `src/firewall/`

Provides read-only discovery, monitoring and in-memory state management for the Linux nftables firewall.

## Discovery and data

Uses `NETLINK_NETFILTER` directly and does not parse external commands such as `nft`, `iptables`, `ufw` or `firewall-cmd`.

Discovery exposes:

- Tables with address family and table name
- Chains with family, table, name, hook, priority, policy and chain type
- Rules with family, table, chain, handle and ordered expressions

Supported semantic rule expressions include metadata, comparisons, counters, immediate values and verdicts. Supported verdicts include accept, drop, continue, break, return, jump, goto, queue, repeat, stolen and stop. Jump and goto expressions can include their target chain.

Interface-name comparisons are decoded only when register context identifies the data as an interface name. Unknown, unsupported or incomplete expressions remain available as structured raw expression data.

## Monitoring and state

Event-driven Netfilter Netlink monitoring detects table, chain and rule additions and removals while preserving kernel event order.

The monitor reports errors for unreliable or malformed event streams. In-memory state uses explicit identities for tables, chains and rules, applies structured events, cascades table and chain removals, and can rebuild a complete discovery snapshot.

## CLI

Run the module with:

```text
python -m src.firewall.main
```

Available options:

- `--list tables` lists nftables tables.
- `--table TABLE` displays chains in a selected table.
- `--family FAMILY` narrows table selection by nftables family.
- `--chain CHAIN` displays rules in a selected chain and requires `--table`.

`--list` and `--table` are mutually exclusive.

Examples:

```text
python -m src.firewall.main
python -m src.firewall.main --list tables
python -m src.firewall.main --table filter
python -m src.firewall.main --table filter --family inet
python -m src.firewall.main --table filter --family inet --chain input
```
