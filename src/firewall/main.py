import argparse

from .cli import (
    print_chains,
    print_not_found,
    print_overview,
    print_rules,
    print_tables,
)
from .discover import discover_firewall


def main() -> None:
    parser = _create_parser()
    arguments = parser.parse_args()

    if arguments.chain is not None and arguments.table is None:
        parser.error("--chain requires --table")

    try:
        tables, chains, rules = discover_firewall()
    except PermissionError as error:
        parser.exit(1, f"error: {error.strerror or error}\n")

    if arguments.list_attribute == "tables":
        print_tables(tables)
        return

    if arguments.table is None:
        print_overview(tables, chains, rules)
        return

    matching_tables = [
        table
        for table in tables
        if table.name == arguments.table
        and (arguments.family is None or table.family == arguments.family)
    ]
    if not matching_tables:
        print_not_found(f"table matching {arguments.table}")
        return

    identities = {(table.family, table.name) for table in matching_tables}
    matching_chains = [
        chain for chain in chains if (chain.family, chain.table) in identities
    ]
    if arguments.chain is None:
        print_chains(matching_chains)
        return

    selected_chains = [
        chain for chain in matching_chains if chain.name == arguments.chain
    ]
    if not selected_chains:
        print_not_found(f"chain matching {arguments.chain}")
        return

    chain_identities = {
        (chain.family, chain.table, chain.name) for chain in selected_chains
    }
    matching_rules = [
        rule
        for rule in rules
        if (rule.family, rule.table, rule.chain) in chain_identities
    ]
    if matching_rules:
        print_rules(matching_rules)
    else:
        print_not_found("rules")


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect Linux nftables state")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--list", dest="list_attribute", choices=("tables",))
    selection.add_argument("--table", help="inspect chains in a table")
    parser.add_argument("--family", help="select an nftables family")
    parser.add_argument("--chain", help="inspect rules in a chain")
    return parser


if __name__ == "__main__":
    main()
