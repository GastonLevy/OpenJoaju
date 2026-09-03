from collections.abc import Iterable
from dataclasses import dataclass

from .discover import discover_neighbors
from .dto import NeighborDTO
from .monitor import NeighborEvent, NeighborEventType


@dataclass(frozen=True)
class _NeighborIdentity:
    family: str
    ip_address: str
    interface_index: int


class NeighborState:
    def __init__(self, neighbors: Iterable[NeighborDTO] | None = None) -> None:
        initial_neighbors = discover_neighbors() if neighbors is None else neighbors
        self._neighbors = {
            _neighbor_identity(neighbor): neighbor for neighbor in initial_neighbors
        }

    def list(self) -> list[NeighborDTO]:
        return list(self._neighbors.values())

    def apply_event(self, event: NeighborEvent) -> bool:
        identity = _neighbor_identity(event.neighbor)
        if event.event_type is NeighborEventType.UPSERTED:
            if self._neighbors.get(identity) == event.neighbor:
                return False
            self._neighbors[identity] = event.neighbor
            return True
        if event.event_type is NeighborEventType.REMOVED:
            return self._neighbors.pop(identity, None) is not None
        return False

    def resynchronize(self) -> bool:
        neighbors = {
            _neighbor_identity(neighbor): neighbor
            for neighbor in discover_neighbors()
        }
        if neighbors == self._neighbors:
            return False
        self._neighbors = neighbors
        return True


def _neighbor_identity(neighbor: NeighborDTO) -> _NeighborIdentity:
    return _NeighborIdentity(
        family=neighbor.family,
        ip_address=neighbor.ip_address,
        interface_index=neighbor.interface_index,
    )
