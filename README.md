<div align="center">

# OpenJoaju

### Lightweight Linux Networking Control Panel

Inspect and manage Linux networking from a simple, modular interface.

![Status](https://img.shields.io/badge/status-early%20development-orange)
![Platform](https://img.shields.io/badge/platform-Debian-A81D33?logo=debian\&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-networking-FCC624?logo=linux\&logoColor=black)
![Python](https://img.shields.io/badge/Python-primary-3776AB?logo=python\&logoColor=white)
![Open Source](https://img.shields.io/badge/open%20source-yes-brightgreen)

</div>

---

## What is OpenJoaju?

OpenJoaju is a lightweight and modular control panel for Linux networking.

It is designed to be installed on an existing Linux system and provide a clear interface for inspecting and eventually managing the networking configuration already present on that machine.

OpenJoaju does not replace Linux networking.

It uses it.

A fresh Debian installation, an existing server, a homelab machine or a Linux router should all be able to run OpenJoaju without requiring the system to be rebuilt around it.

## Why OpenJoaju?

Linux already provides powerful networking capabilities, but inspecting a system often means moving between multiple commands, files and tools.

OpenJoaju aims to provide a single networking-focused view of the system while keeping Linux itself as the source of truth.

The project focuses on:

* lightweight operation;
* modular components;
* existing Linux installations;
* transparent and inspectable code;
* native Linux networking capabilities;
* minimal unnecessary dependencies.

OpenJoaju is not intended to become a general-purpose Linux administration panel.

Its scope is networking.

## Current Direction

The first releases focus on network inspection.

Initial areas include:

* network interfaces;
* IPv4 and IPv6 addresses;
* routing tables;
* routes;
* ARP / NDP neighbors;
* interface state;
* MAC addresses;
* MTU;
* interface statistics;
* IP forwarding state.

The initial MVP targets Debian.

Configuration and modification features will be introduced incrementally after the inspection layer is stable.

## Concept

```text
                    OpenJoaju

                        │
                  Web Interface
                        │
                 Python / Flask
                        │
                Data Collectors
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

OpenJoaju discovers and presents what is actually happening on the machine.

## Existing Systems

OpenJoaju is intended to work with machines that are already configured.

For example, a Linux system may already contain:

```text
Interfaces
├── enp3s0
├── wlan0
├── bridges
└── VLAN interfaces

Routing
├── default route
├── static routes
└── custom routing tables

Networking
├── port forwarding
├── firewall rules
├── network namespaces
└── additional services
```

Installing OpenJoaju should not require recreating that configuration.

The goal is to inspect what is already there and present the relevant networking information in one place.

## Modular by Design

The core project focuses on networking capabilities available on the base Linux system.

Additional integrations can eventually be provided as separate modules.

Possible future modules include:

```text
OpenJoaju
├── Core
├── Web
├── Docker / Containers
├── FRRouting
├── DHCP
├── DNS
└── Monitoring
```

A machine should only need to install the components it actually uses.

For example, a server without Docker should not need Docker-related OpenJoaju components.

## Future Integrations

OpenJoaju may eventually detect networking software already installed on the machine and expose additional information through optional modules.

Examples include:

* Docker and container networking;
* FRRouting;
* OSPF;
* BGP;
* DHCP services;
* DNS services;
* firewall and NAT inspection;
* VPN networking;
* network monitoring.

These integrations are not part of the initial MVP.

## Technology

The project currently favors:

**Backend and system integration**

```text
Python
Linux APIs
Netlink / rtnetlink
Linux sockets
/proc
/sys
```

**Web interface**

```text
Flask
Jinja
HTML
CSS
Minimal JavaScript
```

Low-level components may use C in the future when there is a concrete technical reason for doing so.

## Project Status

OpenJoaju is currently in early development.

The initial goal is to build a reliable read-only view of the networking state of a Debian system before introducing configuration-changing functionality.

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

Contribution guidelines, development setup and issue templates will be added as the project matures.

Bug reports, networking edge cases and implementation discussions will be particularly valuable during the early stages.

---

<div align="center">

**OpenJoaju**

Lightweight. Modular. Linux networking.

</div>
