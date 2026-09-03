from collections.abc import Iterable
from dataclasses import dataclass

from .discover import discover_routes
from .dto import RouteDTO
from .monitor import RouteEvent, RouteEventType


@dataclass(frozen=True)
class _RouteIdentity:
    table: str
    family: str
    destination: str
    gateway: str | None
    interface: str | None
    metric: int | None
    route_type: str


class RouteState:
    def __init__(self, routes: Iterable[RouteDTO] | None = None) -> None:
        initial_routes = discover_routes() if routes is None else routes
        self._routes: dict[_RouteIdentity, RouteDTO] = {}
        for route in initial_routes:
            self._routes[_route_identity(route)] = route

    def list(self) -> list[RouteDTO]:
        return list(self._routes.values())

    def apply_event(self, event: RouteEvent) -> bool:
        if event.event_type is RouteEventType.ADDED:
            return self._add(event.route)
        if event.event_type is RouteEventType.REMOVED:
            return self._remove(event.route)
        return False

    def _add(self, route: RouteDTO) -> bool:
        identity = _route_identity(route)
        if self._routes.get(identity) == route:
            return False
        self._routes[identity] = route
        return True

    def _remove(self, route: RouteDTO) -> bool:
        candidates = [
            identity
            for identity, stored_route in self._routes.items()
            if _matches_removal(stored_route, route)
        ]
        if len(candidates) != 1:
            # A sparse delete must never remove an arbitrary same-destination route.
            return False
        del self._routes[candidates[0]]
        return True


def _route_identity(route: RouteDTO) -> _RouteIdentity:
    return _RouteIdentity(
        table=route.table,
        family=route.family,
        destination=route.destination,
        gateway=route.gateway,
        interface=route.interface,
        metric=route.metric,
        route_type=route.route_type,
    )


def _matches_removal(stored: RouteDTO, removed: RouteDTO) -> bool:
    if (
        stored.table != removed.table
        or stored.family != removed.family
        or stored.destination != removed.destination
        or stored.protocol != removed.protocol
        or stored.scope != removed.scope
        or stored.route_type != removed.route_type
    ):
        return False

    optional_attributes = (
        "gateway",
        "interface",
        "preferred_source",
        "metric",
    )
    return all(
        getattr(removed, attribute) is None
        or getattr(stored, attribute) == getattr(removed, attribute)
        for attribute in optional_attributes
    )
