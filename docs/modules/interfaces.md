# Interfaces

Path: `src/interfaces/`

Provides read-only discovery, monitoring and in-memory state management for Linux network interfaces.

## Discovery and data

Interface-level information is obtained from Linux system interfaces such as `/sys/class/net`. IPv4 and IPv6 addresses are discovered separately through route Netlink and combined into `InterfaceDTO` objects.

Each interface exposes:

- Name and interface index
- Interface type
- Operational and carrier state
- MAC address and MTU
- Link speed and duplex mode
- IPv4 and IPv6 addresses
- RX and TX byte, packet, error and dropped-packet counters

## Monitoring and state

Event-driven route Netlink monitoring detects interface creation and removal, operational-state changes, and IPv4 or IPv6 address additions and removals.

The monitor reports synchronization errors for unreliable or malformed event streams. In-memory state applies structured events and can rebuild a complete snapshot through interface discovery.

## CLI

Run the module with:

```text
python -m src.interfaces.main
```

Available options:

- `--list {name,mac}` lists interface names or MAC addresses.
- `--name NAME` selects an interface by name.
- `--mac ADDRESS` selects an interface by MAC address, case-insensitively.

The selection options are mutually exclusive.

Examples:

```text
python -m src.interfaces.main
python -m src.interfaces.main --list name
python -m src.interfaces.main --list mac
python -m src.interfaces.main --name eno1
python -m src.interfaces.main --mac b8:d4:bc:35:5e:d4
```
