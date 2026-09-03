from dataclasses import dataclass


@dataclass
class RouteDTO:
    table: str
    destination: str
    gateway: str | None
    interface: str | None
    preferred_source: str | None
    metric: int | None
    protocol: str
    scope: str
    route_type: str
    family: str
