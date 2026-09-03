import ipaddress

from .dto import RouteDTO


_HEADERS = (
    "Destination",
    "Gateway",
    "Interface",
    "Source",
    "Metric",
    "Protocol",
    "Scope",
    "Type",
)
_TABLE_PRIORITY = {"local": 0, "main": 1, "default": 2}


def print_grouped_routes(routes: list[RouteDTO]) -> None:
    tables = list_routing_tables(routes)
    for index, table in enumerate(tables):
        if index:
            print()
        print(f"Routing table: {table}")
        print()
        print_routes([route for route in routes if route.table == table])


def print_routing_tables(routes: list[RouteDTO]) -> None:
    for table in list_routing_tables(routes):
        print(table)


def list_routing_tables(routes: list[RouteDTO]) -> list[str]:
    return sorted({route.table for route in routes}, key=_table_sort_key)


def print_routes(routes: list[RouteDTO]) -> None:
    rows = [
        (
            route.destination,
            _format_optional(route.gateway),
            _format_optional(route.interface),
            _format_optional(route.preferred_source),
            _format_optional(route.metric),
            route.protocol,
            route.scope,
            route.route_type,
        )
        for route in sorted(routes, key=_route_sort_key)
    ]
    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(_HEADERS)
    ]
    print(_format_row(_HEADERS, widths))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(_format_row(row, widths))


def print_route(route: RouteDTO) -> None:
    print(f"Table:       {route.table}")
    print(f"Destination: {route.destination}")
    print(f"Gateway:     {_format_optional(route.gateway)}")
    print(f"Interface:   {_format_optional(route.interface)}")
    print(f"Source:      {_format_optional(route.preferred_source)}")
    print(f"Metric:      {_format_optional(route.metric)}")
    print(f"Protocol:    {route.protocol}")
    print(f"Scope:       {route.scope}")
    print(f"Type:        {route.route_type}")
    print(f"Family:      {route.family}")


def print_destination_not_found(table: str, destination: str) -> None:
    print(f"No routes found for destination {destination} in routing table {table}.")


def _format_optional(value: object | None) -> str:
    return str(value) if value is not None else "-"


def _format_row(row: tuple[str, ...], widths: list[int]) -> str:
    return " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))


def _route_sort_key(route: RouteDTO) -> tuple[object, ...]:
    network = ipaddress.ip_network(route.destination, strict=False)
    gateway = ipaddress.ip_address(route.gateway) if route.gateway is not None else None
    preferred_source = (
        ipaddress.ip_address(route.preferred_source)
        if route.preferred_source is not None
        else None
    )
    return (
        0 if route.family == "ipv4" else 1,
        int(network.network_address),
        network.prefixlen,
        -1 if gateway is None else int(gateway),
        route.interface or "",
        -1 if preferred_source is None else int(preferred_source),
        -1 if route.metric is None else route.metric,
        route.protocol,
        route.scope,
        route.route_type,
    )


def _table_sort_key(table: str) -> tuple[int, int | str]:
    if table in _TABLE_PRIORITY:
        return (0, _TABLE_PRIORITY[table])
    try:
        return (1, int(table))
    except ValueError:
        return (2, table)
