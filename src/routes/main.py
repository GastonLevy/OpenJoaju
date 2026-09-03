import argparse
import ipaddress

from .cli import (
    list_routing_tables,
    print_destination_not_found,
    print_grouped_routes,
    print_route,
    print_routes,
    print_routing_tables,
)
from .discover import discover_routes


def main() -> None:
    parser = _create_parser()
    arguments = parser.parse_args()

    if arguments.destination is not None and arguments.table is None:
        parser.error("--destination requires --table")

    routes = discover_routes()

    if arguments.list_attribute == "tables":
        print_routing_tables(routes)
        return

    if arguments.table is not None:
        table = _find_table(arguments.table, list_routing_tables(routes))
        if table is None:
            parser.error(f"routing table not found: {arguments.table}")

        table_routes = [route for route in routes if route.table == table]
        if arguments.destination is None:
            print_routes(table_routes)
            return

        matching_routes = [
            route
            for route in table_routes
            if route.destination == arguments.destination
        ]
        if len(matching_routes) == 1:
            print_route(matching_routes[0])
        elif matching_routes:
            print_routes(matching_routes)
        else:
            print_destination_not_found(table, arguments.destination)
        return

    print_grouped_routes(routes)


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Display network routes")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--list", dest="list_attribute", choices=("tables",)
    )
    selection.add_argument("--table", help="display one routing table by name or ID")
    parser.add_argument(
        "--destination",
        type=_normalized_destination,
        help="filter a routing table by exact destination prefix",
    )
    return parser


def _normalized_destination(value: str) -> str:
    try:
        return str(ipaddress.ip_network(value, strict=False))
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid destination prefix: {value}") from error


def _find_table(requested: str, tables: list[str]) -> str | None:
    aliases = {"253": "default", "254": "main", "255": "local"}
    requested_table = aliases.get(requested, requested)
    return next(
        (table for table in tables if table.casefold() == requested_table.casefold()),
        None,
    )


if __name__ == "__main__":
    main()
