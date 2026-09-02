# OpenJoaju Architecture

## Module structure

Every networking module lives under `src/` and must contain its own discovery, monitoring, data representation and CLI presentation logic.

Required structure:

```text
src/
└── <module>/
    ├── __init__.py
    ├── dto.py
    ├── discover/
    │   └── __init__.py
    ├── monitor.py
    ├── cli.py
    └── main.py
```

## dto.py

Every module must provide its own `dto.py`.

`dto.py` defines the structured data objects exposed by the module.

Discovery and monitoring components should return or work with these objects instead of formatted text.

DTOs must remain independent from presentation layers such as CLI, HTML or API output.

## discover/

Every module must provide its own `discover/` package.

The discovery package is responsible for obtaining a complete snapshot of the current Linux networking state related to that module.

A module must not depend on another module to discover its own state.

Discovery must be read-only and must not modify system configuration.

Discovery logic should be split into separate files when responsibilities become distinct.

Example:

```text
src/
└── interfaces/
    └── discover/
        ├── __init__.py
        ├── links.py
        └── addresses.py
```

In this case:

- `links.py` handles interface-level information such as name, operational state, MAC address and MTU.
- `addresses.py` handles IPv4 and IPv6 addresses.

`discover/__init__.py` acts as the public entry point for the discovery package and coordinates the internal discovery components.

The rest of the module should not need to know how discovery is internally divided.

## monitor.py

Every module must provide its own `monitor.py`.

`monitor.py` is responsible for detecting changes related to the module after the initial discovery.

Whenever the Linux kernel or another underlying component provides an event-based mechanism, the monitor should subscribe to those events instead of continuously polling the system.

The monitor must detect creation, removal and modification of resources relevant to the module.

The monitor may use the discovery package to obtain the initial state or to rebuild the complete state when synchronization is lost.

Monitoring logic should work with the module's DTOs and must remain independent from presentation layers.

## cli.py

Every module must provide its own `cli.py`.

`cli.py` is responsible only for presenting the module's data in a human-readable command-line format.

It must receive structured data from the module and must not perform system discovery itself.

CLI formatting must remain separate from discovery and monitoring logic.

## main.py

`main.py` is the entry point for running the module directly.

It coordinates the module's discovery, monitoring and CLI presentation as required.

Presentation-specific logic must not be implemented directly in `main.py`.