import argparse
import ipaddress

from .cli import print_neighbors
from .discover import discover_neighbors
from .dto import NeighborDTO


def main() -> None:
    parser = _create_parser()
    arguments = parser.parse_args()
    neighbors = discover_neighbors()
    print_neighbors(_filter_neighbors(neighbors, arguments))


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Display network neighbors")
    parser.add_argument(
        "--all",
        dest="show_all",
        action="store_true",
        help="include multicast, loopback, and other non-host entries",
    )
    parser.add_argument("--family", choices=("ipv4", "ipv6"))
    parser.add_argument("--interface", help="filter by interface name")
    parser.add_argument("--state", type=str.casefold, help="filter by neighbor state")
    parser.add_argument(
        "--ip",
        type=_normalized_ip_address,
        help="filter by exact IP address",
    )
    return parser


def _normalized_ip_address(value: str) -> str:
    try:
        return str(ipaddress.ip_address(value))
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid IP address: {value}") from error


def _filter_neighbors(
    neighbors: list[NeighborDTO], arguments: argparse.Namespace
) -> list[NeighborDTO]:
    matching = [
        neighbor
        for neighbor in neighbors
        if (arguments.family is None or neighbor.family == arguments.family)
        and (arguments.interface is None or neighbor.interface == arguments.interface)
        and (arguments.state is None or neighbor.state.casefold() == arguments.state)
        and (arguments.ip is None or neighbor.ip_address == arguments.ip)
    ]
    if (
        arguments.show_all
        or arguments.state is not None
        or arguments.ip is not None
        or arguments.interface is not None
    ):
        return matching
    return [neighbor for neighbor in matching if _is_host_neighbor(neighbor)]


def _is_host_neighbor(neighbor: NeighborDTO) -> bool:
    address = ipaddress.ip_address(neighbor.ip_address)
    return (
        neighbor.interface != "lo"
        and not address.is_multicast
        and not address.is_unspecified
        and not address.is_loopback
    )


if __name__ == "__main__":
    main()
