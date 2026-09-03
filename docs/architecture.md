# OpenJoaju Architecture

## Module structure

Every networking module lives under `src/` and must contain its own discovery, monitoring, state management, data representation and CLI presentation logic.

Required structure:

    src/
    └── <module>/
        ├── __init__.py
        ├── dto.py
        ├── discover/
        │   └── __init__.py
        ├── monitor.py
        ├── state.py
        ├── cli.py
        └── main.py

## Module independence

Networking modules must remain independent from each other.

A module must not import or depend on another networking module under `src/` for discovery, monitoring, state management or presentation.

Each module is responsible for obtaining and maintaining the Linux networking state required for its own functionality.

If multiple modules require the same underlying system information, each module must obtain the information it needs independently rather than creating runtime dependencies between networking modules.

## dto.py

Every module must provide its own `dto.py`.

`dto.py` defines the structured data objects exposed by the module.

Discovery, monitoring and state management components should return or work with these objects instead of formatted text.

DTOs must remain independent from presentation layers such as CLI, HTML or API output.

## discover/

Every module must provide its own `discover/` package.

The discovery package is responsible for obtaining a complete snapshot of the current Linux networking state related to that module.

Discovery must be read-only and must not modify system configuration.

Discovery logic should be split into separate files when responsibilities become distinct.

Example:

    src/
    └── interfaces/
        └── discover/
            ├── __init__.py
            ├── links.py
            └── addresses.py

In this case:

- `links.py` handles interface-level information such as name, operational state, MAC address and MTU.
- `addresses.py` handles IPv4 and IPv6 addresses.

`discover/__init__.py` acts as the public entry point for the discovery package and coordinates the internal discovery components.

The rest of the module should not need to know how discovery is internally divided.

## monitor.py

Every module must provide its own `monitor.py`.

`monitor.py` is responsible for detecting changes related to the module after the initial discovery.

Whenever the Linux kernel or another underlying component provides an event-based mechanism, the monitor should subscribe to those events instead of continuously polling the system.

The monitor must detect the relevant creation, removal and change events exposed by the underlying system for that module.

Monitoring must expose structured events rather than presentation-specific output.

Event types must use module-specific `StrEnum` values instead of free-form strings.

The underlying string values of event types should remain stable and suitable for serialization by higher-level integration layers.

Example:

    class RouteEventType(StrEnum):
        ADDED = "route_added"
        REMOVED = "route_removed"

Event objects should be immutable when practical and should carry the structured data required to describe the event.

The monitor may use the module's own discovery package to obtain the initial state or to rebuild the complete state when synchronization is lost.

If event delivery becomes unreliable or synchronization with the underlying system is lost, the module must not continue silently with potentially stale state.

When practical, the module should rebuild its complete state using its own discovery package.

Monitoring logic should work with the module's DTOs and must remain independent from presentation layers.

## state.py

Every module must provide its own `state.py`.

`state.py` is responsible for maintaining the module's current in-memory state.

The initial state should normally be obtained from the module's discovery package, while allowing an existing structured snapshot to be supplied when appropriate.

After initialization, the state should be updated using structured events produced by the module's monitor rather than continuously rediscovering the complete system state.

Each module should define explicit internal identities for the objects it tracks so that additions, replacements and removals can be applied deterministically.

Applying an event should indicate whether the in-memory state actually changed.

State management must work with the module's DTOs and event types.

`state.py` must not perform presentation formatting and must remain independent from CLI, HTML, API or other presentation layers.

A module's state must not depend on another networking module.

## cli.py

Every module must provide its own `cli.py`.

`cli.py` is responsible only for presenting the module's data in a human-readable command-line format.

It must receive structured data from the module and must not perform system discovery itself.

CLI formatting must remain separate from discovery, monitoring and state management logic.

## main.py

`main.py` is the entry point for running the module directly.

It coordinates the module's discovery, monitoring, state management and CLI presentation as required.

Presentation-specific logic must not be implemented directly in `main.py`.