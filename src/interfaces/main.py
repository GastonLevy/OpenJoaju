import argparse

from .cli import (
    print_interface,
    print_interface_names,
    print_interfaces,
    print_mac_addresses,
)
from .discover import discover_interfaces
from .discover.links import discover_links


def main() -> None:
    parser = _create_parser()
    arguments = parser.parse_args()

    if arguments.list_attribute == "name":
        print_interface_names(discover_links())
    elif arguments.list_attribute == "mac":
        print_mac_addresses(discover_links())
    else:
        interfaces = discover_interfaces()

        if arguments.name is not None:
            interface = next(
                (item for item in interfaces if item.name == arguments.name), None
            )
            if interface is None:
                parser.error(f"interface not found: {arguments.name}")
            print_interface(interface)
        elif arguments.mac is not None:
            interface = next(
                (
                    item
                    for item in interfaces
                    if item.mac_address.casefold() == arguments.mac.casefold()
                ),
                None,
            )
            if interface is None:
                parser.error(f"interface not found: {arguments.mac}")
            print_interface(interface)
        else:
            print_interfaces(interfaces)


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Display network interfaces")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--list", dest="list_attribute", choices=("name", "mac"))
    selection.add_argument("--name", help="find an interface by name")
    selection.add_argument("--mac", help="find an interface by MAC address")
    return parser


if __name__ == "__main__":
    main()
