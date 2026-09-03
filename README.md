<p align="center">
  <img src="assets/openjoaju-logo.png" width="180" alt="OpenJoaju Logo">
</p>

<h1 align="center">OpenJoaju</h1>

<p align="center">
  Lightweight, modular Linux network management.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-early%20development-orange" alt="Status">
  <img src="https://img.shields.io/badge/platform-Debian-A81D33?logo=debian&logoColor=white" alt="Debian">
  <img src="https://img.shields.io/badge/Linux-networking-FCC624?logo=linux&logoColor=black" alt="Linux">
  <img src="https://img.shields.io/badge/Python-primary-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/open%20source-yes-brightgreen" alt="Open Source">
</p>

---

## What is OpenJoaju?

OpenJoaju is a lightweight and modular Linux network management project.

It runs on an existing Linux system and provides structured discovery, real-time monitoring, state tracking, and human-readable inspection of the networking configuration already present on the machine.

**OpenJoaju does not replace Linux networking. It uses it.**

Linux remains the source of truth. OpenJoaju reads native Linux interfaces such as Netlink, `/proc`, and `/sys` to understand what the system is actually doing.

The project is currently read-only. Configuration-changing functionality will only be introduced after the inspection and monitoring foundation is stable.

## Why OpenJoaju?

Linux already provides powerful networking capabilities, but understanding the complete state of a machine often means moving between multiple commands, kernel interfaces, files, and networking tools.

OpenJoaju aims to provide a single networking-focused view while preserving the Linux system underneath.

The project focuses on:

- native Linux networking capabilities;
- compatibility with existing Linux installations;
- independent and modular components;
- event-driven monitoring instead of unnecessary polling;
- structured networking data;
- minimal external dependencies;
- transparent and inspectable code.

OpenJoaju is not intended to become a general-purpose Linux administration panel.

Its scope is networking.

## What Works Today?

OpenJoaju currently implements three independent networking modules.

### Interfaces

Read-only discovery and real-time monitoring of Linux network interfaces.

Currently includes interface state, type, MAC address, MTU, IPv4/IPv6 addresses, carrier information, link speed, duplex mode, traffic statistics, address changes, and in-memory state tracking.

Interface and address changes are received directly from the Linux kernel through Netlink.

### Routes

Read-only discovery and real-time monitoring of Linux routing tables.

Currently includes IPv4 and IPv6 routes, routing tables, destination prefixes, gateways, output interfaces, preferred sources, metrics, protocols, scopes, route types, multipath routes, and in-memory routing state.

Route discovery and monitoring use native Netlink rather than parsing `ip route` output.

### Firewall

Read-only discovery and real-time monitoring of Linux nftables configuration.

Currently includes nftables tables, chains, rules, structured rule expressions, semantic decoding of supported expressions, and in-memory firewall state.

Firewall discovery and monitoring communicate directly with the kernel through Netfilter Netlink rather than parsing `nft`, `iptables`, `ufw`, or `firewall-cmd` output.

## Architecture

Each networking area is implemented as an independent module.

```text
                    OpenJoaju
                        │
                 Presentation
                        │
                  Module State
                        │
              Discovery + Monitoring
                        │
        ┌───────────────┼───────────────┐
        │               │               │
     Netlink          /proc            /sys
        │               │               │
        └───────────────┼───────────────┘
                        │
                     Linux
```

Each module owns its own:

```text
<module>/
│
├── dto.py
├── discover/
├── monitor.py
├── state.py
├── cli.py
└── main.py
```

Modules do not depend on each other for networking discovery, monitoring, state management, or presentation.

Discovery creates a complete snapshot of the relevant Linux state.

Monitoring receives changes from the kernel as they happen.

State combines both into a current structured representation of the system.

If an event stream becomes unreliable, OpenJoaju detects the synchronization loss rather than silently continuing with potentially stale state. The affected module can rebuild its state from a fresh discovery snapshot.

## Quick Start

OpenJoaju currently targets Debian and requires Python.

Clone the repository:

```bash
git clone https://github.com/GastonLevy/OpenJoaju.git
cd OpenJoaju
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Run interface inspection:

```bash
python -m src.interfaces.main
```

Run routing inspection:

```bash
python -m src.routes.main
```

Run firewall inspection:

```bash
python -m src.firewall.main
```

Some Linux networking information may require appropriate system permissions.

### Examples

List interface names:

```bash
python -m src.interfaces.main --list names
```

Inspect a specific interface:

```bash
python -m src.interfaces.main --name eth0
```

List routing tables:

```bash
python -m src.routes.main --list tables
```

Inspect the main routing table:

```bash
python -m src.routes.main --table main
```

List nftables tables:

```bash
python -m src.firewall.main --list tables
```

Inspect an nftables table:

```bash
python -m src.firewall.main --family ip --table filter
```

## Design Principles

OpenJoaju follows a few core principles:

**Linux remains the source of truth.**  
OpenJoaju observes the networking state that already exists on the machine.

**Native interfaces first.**  
When practical, kernel interfaces and the Python standard library are preferred over parsing external command output.

**Event-driven monitoring.**  
When Linux provides an appropriate event mechanism, OpenJoaju uses it instead of continuous polling.

**Independent modules.**  
Networking modules own their discovery, monitoring, state, and presentation logic without depending on other networking modules.

**Structured data.**  
Internal networking state is represented using structured DTOs rather than CLI-formatted text.

**Read-only first.**  
Reliable inspection and monitoring come before configuration-changing functionality.

## Roadmap

Potential future networking areas include:

- ARP and NDP neighbors;
- VLANs;
- bridges;
- bonding;
- IP forwarding state;
- network namespaces;
- NAT inspection;
- VPN networking.

Potential optional integrations may later include:

- Docker and container networking;
- FRRouting;
- OSPF;
- BGP;
- DHCP services;
- DNS services;
- network monitoring systems.

These are future areas and are not part of the currently implemented core.

## Technology

OpenJoaju currently favors:

```text
Python
Linux APIs
Netlink / rtnetlink
Netfilter Netlink
Linux sockets
/proc
/sys
```

The Python standard library and native Linux interfaces are preferred where practical.

External dependencies should only be introduced when they provide a clear technical benefit.

## Project Status

OpenJoaju is in **early development**.

The current foundation provides working read-only discovery, event-driven monitoring, and in-memory state management for:

- network interfaces;
- routing tables and routes;
- nftables firewall state.

The initial target platform is Debian.

Breaking changes should be expected while the architecture and module set continue to evolve.

## Documentation

More detailed technical documentation is available under `docs/`:

- [`docs/architecture.md`](docs/architecture.md) — architecture and module design rules.
- [`docs/modules.md`](docs/modules.md) — currently implemented modules and their capabilities.

## Philosophy

```text
Do not replace Linux.

Understand it.

Expose it.

Make it easier to operate.
```

## Contributing

OpenJoaju is being developed openly.

Contribution guidelines, development setup, and issue templates will be expanded as the project matures.

Bug reports, Linux networking edge cases, compatibility findings, and implementation discussions are particularly valuable during early development.

---

<div align="center">

**OpenJoaju**

Lightweight. Modular. Linux networking.

</div>