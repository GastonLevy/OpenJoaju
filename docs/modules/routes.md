# Routes

Path: `src/routes/`

Provides read-only discovery, monitoring and in-memory state management for Linux routing tables.

## Discovery and data

Uses `NETLINK_ROUTE` directly and does not parse external commands such as `ip route`. IPv4 and IPv6 routes are supported, and multipath routes are represented as individual entries for their next hops.

Each `RouteDTO` exposes:

- Routing table
- Destination prefix
- Gateway
- Output interface
- Preferred source
- Metric
- Routing protocol
- Scope
- Route type
- Address family

Standard tables are represented as `local`, `main` and `default`. Custom tables use their numeric identifier.

## Monitoring and state

Event-driven route Netlink monitoring detects route additions and removals. Structured `RouteEvent` objects use `RouteEventType` values.

The monitor reports synchronization errors for unreliable or malformed event streams. In-memory state uses explicit route identities, applies additions and removals deterministically, and can rebuild a complete snapshot through route discovery.

## CLI

Run the module with:

```text
python -m src.routes.main
```

Available options:

- `--list tables` lists routing tables.
- `--table TABLE` selects a routing table by name or numeric identifier.
- `--destination PREFIX` filters the selected table by an exact normalized destination prefix and requires `--table`.

Routes are displayed with deterministic ordering, with IPv4 before IPv6.

Examples:

```text
python -m src.routes.main
python -m src.routes.main --list tables
python -m src.routes.main --table main
python -m src.routes.main --table 254
python -m src.routes.main --table main --destination 0.0.0.0/0
```
