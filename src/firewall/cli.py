from .dto import (
    ChainDTO,
    ComparisonExpressionDTO,
    CounterExpressionDTO,
    ExpressionAttributeDTO,
    ExpressionDTO,
    ImmediateExpressionDTO,
    MetaExpressionDTO,
    RuleDTO,
    RuleExpressionDTO,
    TableDTO,
    VerdictExpressionDTO,
)


def print_overview(
    tables: list[TableDTO],
    chains: list[ChainDTO],
    rules: list[RuleDTO],
) -> None:
    if not tables:
        print("No nftables tables found.")
        return

    for index, table in enumerate(_sorted_tables(tables)):
        if index:
            print()
        table_chains = [
            chain
            for chain in chains
            if chain.family == table.family and chain.table == table.name
        ]
        table_rules = [
            rule
            for rule in rules
            if rule.family == table.family and rule.table == table.name
        ]
        print(f"Firewall table: {table.family} {table.name}")
        print(f"Chains: {len(table_chains)}")
        print(f"Rules:  {len(table_rules)}")


def print_tables(tables: list[TableDTO]) -> None:
    for table in _sorted_tables(tables):
        print(f"{table.family} {table.name}")


def print_chains(chains: list[ChainDTO]) -> None:
    headers = ("Family", "Table", "Chain", "Type", "Hook", "Priority", "Policy")
    rows = [
        (
            chain.family,
            chain.table,
            chain.name,
            _optional(chain.chain_type),
            _optional(chain.hook),
            _optional(chain.priority),
            _optional(chain.policy),
        )
        for chain in sorted(chains, key=lambda item: (item.family, item.table, item.name))
    ]
    _print_table(headers, rows)


def print_rules(rules: list[RuleDTO]) -> None:
    for rule_index, rule in enumerate(
        sorted(
            rules,
            key=lambda item: (
                item.family,
                item.table,
                item.chain,
                -1 if item.handle is None else item.handle,
            ),
        )
    ):
        if rule_index:
            print()
        print(f"Family: {rule.family}")
        print(f"Table:  {rule.table}")
        print(f"Chain:  {rule.chain}")
        print(f"Handle: {_optional(rule.handle)}")
        print("Expressions:")
        if not rule.expressions:
            print("  -")
            continue
        for expression in rule.expressions:
            _print_expression(expression)


def print_not_found(resource: str) -> None:
    print(f"No nftables {resource} found.")


def _print_expression(expression: RuleExpressionDTO) -> None:
    if isinstance(expression, MetaExpressionDTO):
        print("  meta")
        print(f"    key: {expression.key}")
        print(
            "    destination register: "
            f"{_optional(expression.destination_register)}"
        )
        print(f"    source register: {_optional(expression.source_register)}")
    elif isinstance(expression, ComparisonExpressionDTO):
        print("  comparison")
        print(f"    source register: {expression.source_register}")
        print(f"    operation: {expression.operation}")
        label = (
            "interface name"
            if expression.data_type == "interface_name"
            else "data"
        )
        value = (
            f"0x{expression.data.hex()}"
            if isinstance(expression.data, bytes)
            else expression.data
        )
        print(f"    {label}: {value}")
    elif isinstance(expression, CounterExpressionDTO):
        print("  counter")
        print(f"    packets: {expression.packets}")
        print(f"    bytes: {expression.bytes}")
    elif isinstance(expression, VerdictExpressionDTO):
        print("  verdict")
        print(f"    action: {expression.action}")
        if expression.chain is not None:
            print(f"    chain: {expression.chain}")
        if expression.chain_id is not None:
            print(f"    chain ID: {expression.chain_id}")
    elif isinstance(expression, ImmediateExpressionDTO):
        print("  immediate")
        print(f"    destination register: {expression.destination_register}")
        print(f"    data: 0x{expression.data.hex()}")
    elif isinstance(expression, ExpressionDTO):
        print(f"  {expression.name}")
        if not expression.attributes:
            print("    -")
        else:
            _print_attributes(expression.attributes, indent=4)


def _print_attributes(
    attributes: tuple[ExpressionAttributeDTO, ...], *, indent: int
) -> None:
    prefix = " " * indent
    for attribute in attributes:
        flags = []
        if attribute.nested:
            flags.append("nested")
        if attribute.network_byte_order:
            flags.append("network-byte-order")
        suffix = f" ({', '.join(flags)})" if flags else ""
        if isinstance(attribute.value, tuple):
            print(f"{prefix}attribute {attribute.attribute_type}{suffix}:")
            _print_attributes(attribute.value, indent=indent + 2)
        else:
            print(
                f"{prefix}attribute {attribute.attribute_type}{suffix}: "
                f"0x{attribute.value.hex()}"
            )


def _print_table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]
    print(_format_row(headers, widths))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(_format_row(row, widths))


def _format_row(row: tuple[str, ...], widths: list[int]) -> str:
    return " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))


def _optional(value: object | None) -> str:
    return "-" if value is None else str(value)


def _sorted_tables(tables: list[TableDTO]) -> list[TableDTO]:
    return sorted(tables, key=lambda item: (item.family, item.name))
