import ipaddress

from .dto import NeighborDTO


_HEADERS = ("IP address", "MAC address", "Interface", "Index", "Family", "State")


def print_neighbors(neighbors: list[NeighborDTO]) -> None:
    rows = [
        (
            neighbor.ip_address,
            _format_optional(neighbor.mac_address),
            _format_optional(neighbor.interface),
            str(neighbor.interface_index),
            neighbor.family,
            neighbor.state.upper(),
        )
        for neighbor in sorted(neighbors, key=_neighbor_sort_key)
    ]
    widths = [
        max([len(header), *(len(row[index]) for row in rows)])
        for index, header in enumerate(_HEADERS)
    ]
    print(_format_row(_HEADERS, widths))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(_format_row(row, widths))


def _format_optional(value: object | None) -> str:
    return str(value) if value is not None else "-"


def _format_row(row: tuple[str, ...], widths: list[int]) -> str:
    return " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))


def _neighbor_sort_key(neighbor: NeighborDTO) -> tuple[object, ...]:
    address = ipaddress.ip_address(neighbor.ip_address)
    return (
        0 if neighbor.family == "ipv4" else 1,
        int(address),
        neighbor.interface_index,
        neighbor.mac_address or "",
        neighbor.state,
    )
