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

It is designed to be installed on an existing Linux system and provide a clear interface for inspecting and eventually managing the networking configuration already present on that machine.

OpenJoaju does not replace Linux networking.

It uses it.

A fresh Debian installation, an existing server, a homelab machine, or a Linux router should all be able to run OpenJoaju without requiring the system to be rebuilt around it.

## Why OpenJoaju?

Linux already provides powerful networking capabilities, but inspecting a system often means moving between multiple commands, files, APIs, and tools.

OpenJoaju aims to provide a single networking-focused view of the system while keeping Linux itself as the source of truth.

The project focuses on:

- lightweight operation;
- modular components;
- existing Linux installations;
- transparent and inspectable code;
- native Linux networking capabilities;
- minimal unnecessary dependencies.

OpenJoaju is not intended to become a general-purpose Linux administration panel.

Its scope is networking.

## Current Development

The project is currently focused on building a reliable read-only networking inspection and monitoring layer.

The interfaces module currently provides:

- network interface discovery;
- interface type detection;
- operational state;
- MAC addresses;
- MTU;
- IPv4 and IPv6 addresses with prefix lengths;
- interface index;
- carrier state;
- link speed;
- duplex information;
- RX/TX statistics;
- interface lookup by name or MAC address;
- real-time interface monitoring through Netlink;
- IPv4 and IPv6 address change monitoring;
- in-memory interface state tracking.

Interface and address changes are received directly from the Linux kernel through Netlink rather than through continuous polling.

Planned core areas include:

- routing tables;
- routes;
- ARP / NDP neighbors;
- IP forwarding state;
- VLANs;
- bridges;
- bonding;
- network namespaces;
- firewall and NAT inspection.

The initial MVP targets Debian.

Configuration-changing features will be introduced incrementally after the inspection and monitoring layers are stable.

## Concept

```text
                    OpenJoaju
                        │
              Presentation Layers
                CLI / Web / API
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

Linux remains responsible for networking.

OpenJoaju discovers, monitors, and presents what is actually happening on the machine.

## Existing Systems

OpenJoaju is intended to work with machines that are already configured.

For example, a Linux system may already contain:

```text
Interfaces
├── Ethernet
├── Wi-Fi
├── bridges
├── VLAN interfaces
└── virtual interfaces

Routing
├── default routes
├── static routes
└── custom routing tables

Networking
├── port forwarding
├── firewall rules
├── network namespaces
└── additional services
```

Installing OpenJoaju should not require recreating that configuration.

The goal is to discover what is already there, monitor changes, and present the relevant networking information in one place.

## Modular by Design

Networking functionality is divided into independent modules.

Each module is responsible for discovering and monitoring its own Linux networking state while exposing structured data that can later be consumed by different presentation layers.

Conceptually:

```text
OpenJoaju
│
├── Interfaces
├── Routes
├── Neighbors
├── Firewall / NAT
├── Namespaces
│
└── Optional Integrations
    ├── Docker / Containers
    ├── FRRouting
    ├── DHCP
    ├── DNS
    └── Monitoring
```

A machine should only need the components relevant to the networking functionality it actually uses.

For example, a server without Docker should not require Docker-specific OpenJoaju components.

## Interface Architecture

The current interfaces module separates system discovery, monitoring, state, and presentation.

```text
interfaces/
│
├── dto.py
│
├── discover/
│   ├── links.py
│   └── addresses.py
│
├── monitor.py
├── state.py
├── cli.py
└── main.py
```

The general flow is:

```text
Linux
  │
  ├── Initial discovery
  │        │
  │        ▼
  │   InterfaceState
  │        ▲
  │        │
  └── Netlink events
           │
           ▼
        monitor.py
```

Discovery builds the initial snapshot.

The monitor subscribes to Linux kernel events.

The state layer determines whether those events actually change OpenJoaju's current representation of the system.

Presentation layers remain independent from the underlying Linux discovery and monitoring implementation.

## Future Integrations

OpenJoaju may eventually detect networking software already installed on the machine and expose additional capabilities through optional modules.

Potential integrations include:

- Docker and container networking;
- FRRouting;
- OSPF;
- BGP;
- DHCP services;
- DNS services;
- firewall and NAT management;
- VPN networking;
- network monitoring.

These integrations are not part of the initial MVP.

## Technology

### Backend and system integration

```text
Python
Linux APIs
Netlink / rtnetlink
Linux sockets
/proc
/sys
```

The project currently favors the Python standard library and native Linux interfaces where practical.

External dependencies should only be introduced when they provide a clear technical benefit.

### Web interface

The planned web layer currently favors:

```text
Flask
Jinja
HTML
CSS
Minimal JavaScript
```

The web interface will consume structured OpenJoaju data rather than executing or parsing CLI output.

Low-level components may use C in the future when there is a concrete technical reason for doing so.

## Project Status

OpenJoaju is currently in early development.

The interface discovery, inspection, Netlink monitoring, and in-memory state foundations are under active development.

The initial objective is to build a reliable read-only representation of Linux networking before introducing configuration-changing functionality.

Expect breaking changes while the architecture is being established.

## Philosophy

```text
Do not replace Linux.

Understand it.

Expose it.

Make it easier to operate.
```

## Contributing

OpenJoaju is being developed openly.

Contribution guidelines, development setup, and issue templates will be added as the project matures.

Bug reports, networking edge cases, Linux compatibility findings, and implementation discussions will be particularly valuable during the early stages.

---

<div align="center">

**OpenJoaju**

Lightweight. Modular. Linux networking.

</div>