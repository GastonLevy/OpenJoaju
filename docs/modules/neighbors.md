# Neighbors

Path: `src/neighbors/`

Provides read-only discovery, monitoring and in-memory state management for the Linux neighbor table, including IPv4 ARP and IPv6 NDP neighbors.

## Discovery and data

Uses `NETLINK_ROUTE` directly to obtain the complete kernel neighbor table.

Each `NeighborDTO` exposes:

- IP address
- MAC address, when available
- Interface name, when available
- Interface index
- Address family
- Neighbor state

## Monitoring and state

Event-driven `RTMGRP_NEIGH` monitoring detects neighbor changes. Structured neighbor events use `UPSERTED` for additions or updates and `REMOVED` for removals.

The monitor reports synchronization errors for unreliable or malformed event streams. In-memory state identifies neighbors by address family, IP address and interface index, and can rebuild a complete snapshot through neighbor discovery.

## CLI

Run the module with:

```text
python -m src.neighbors.main
```

By default, the CLI displays useful host neighbors while hiding multicast, unspecified and loopback entries. `--all` displays the complete discovered neighbor table.

Available options and filters:

- `--all` includes multicast, loopback and other non-host entries.
- `--family {ipv4,ipv6}` filters by address family.
- `--interface NAME` filters by interface name.
- `--state STATE` filters by neighbor state, case-insensitively.
- `--ip ADDRESS` filters by an exact normalized IP address.

Filters can be combined. Explicit `--interface`, `--state` and `--ip` filters include matching entries that the default useful-host view would hide.

Examples:

```text
python -m src.neighbors.main
python -m src.neighbors.main --all
python -m src.neighbors.main --family ipv4
python -m src.neighbors.main --interface eno1
python -m src.neighbors.main --state reachable
python -m src.neighbors.main --ip 192.168.0.1
```
