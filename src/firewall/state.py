from dataclasses import dataclass

from .discover import discover_firewall
from .dto import ChainDTO, RuleDTO, TableDTO
from .monitor import FirewallEvent, FirewallEventType


FirewallSnapshot = tuple[list[TableDTO], list[ChainDTO], list[RuleDTO]]


@dataclass(frozen=True)
class _TableIdentity:
    family: str
    name: str


@dataclass(frozen=True)
class _ChainIdentity:
    family: str
    table: str
    name: str


@dataclass(frozen=True)
class _RuleIdentity:
    family: str
    table: str
    chain: str
    handle: int | None


class FirewallState:
    def __init__(self, snapshot: FirewallSnapshot | None = None) -> None:
        self._tables: dict[_TableIdentity, TableDTO] = {}
        self._chains: dict[_ChainIdentity, ChainDTO] = {}
        self._rules: dict[_RuleIdentity, RuleDTO] = {}
        self._replace_snapshot(discover_firewall() if snapshot is None else snapshot)

    def list_tables(self) -> list[TableDTO]:
        return list(self._tables.values())

    def list_chains(self) -> list[ChainDTO]:
        return list(self._chains.values())

    def list_rules(self) -> list[RuleDTO]:
        return list(self._rules.values())

    def apply_event(self, event: FirewallEvent) -> bool:
        if event.event_type is FirewallEventType.TABLE_ADDED:
            return self._add_table(event.item)
        if event.event_type is FirewallEventType.TABLE_REMOVED:
            return self._remove_table(event.item)
        if event.event_type is FirewallEventType.CHAIN_ADDED:
            return self._add_chain(event.item)
        if event.event_type is FirewallEventType.CHAIN_REMOVED:
            return self._remove_chain(event.item)
        if event.event_type is FirewallEventType.RULE_ADDED:
            return self._add_rule(event.item)
        if event.event_type is FirewallEventType.RULE_REMOVED:
            return self._remove_rule(event.item)
        return False

    def resynchronize(self) -> bool:
        snapshot = discover_firewall()
        if snapshot == (
            self.list_tables(),
            self.list_chains(),
            self.list_rules(),
        ):
            return False
        self._replace_snapshot(snapshot)
        return True

    def _replace_snapshot(self, snapshot: FirewallSnapshot) -> None:
        tables, chains, rules = snapshot
        self._tables = {_table_identity(table): table for table in tables}
        self._chains = {_chain_identity(chain): chain for chain in chains}
        self._rules = {_rule_identity(rule): rule for rule in rules}

    def _add_table(self, item: TableDTO | ChainDTO | RuleDTO) -> bool:
        if not isinstance(item, TableDTO):
            return False
        identity = _table_identity(item)
        if self._tables.get(identity) == item:
            return False
        self._tables[identity] = item
        return True

    def _remove_table(self, item: TableDTO | ChainDTO | RuleDTO) -> bool:
        if not isinstance(item, TableDTO):
            return False
        identity = _table_identity(item)
        changed = self._tables.pop(identity, None) is not None
        chain_identities = [
            chain_identity
            for chain_identity in self._chains
            if chain_identity.family == item.family
            and chain_identity.table == item.name
        ]
        rule_identities = [
            rule_identity
            for rule_identity in self._rules
            if rule_identity.family == item.family
            and rule_identity.table == item.name
        ]
        for chain_identity in chain_identities:
            del self._chains[chain_identity]
        for rule_identity in rule_identities:
            del self._rules[rule_identity]
        return changed or bool(chain_identities) or bool(rule_identities)

    def _add_chain(self, item: TableDTO | ChainDTO | RuleDTO) -> bool:
        if not isinstance(item, ChainDTO):
            return False
        identity = _chain_identity(item)
        if self._chains.get(identity) == item:
            return False
        self._chains[identity] = item
        return True

    def _remove_chain(self, item: TableDTO | ChainDTO | RuleDTO) -> bool:
        if not isinstance(item, ChainDTO):
            return False
        identity = _chain_identity(item)
        changed = self._chains.pop(identity, None) is not None
        rule_identities = [
            rule_identity
            for rule_identity in self._rules
            if rule_identity.family == item.family
            and rule_identity.table == item.table
            and rule_identity.chain == item.name
        ]
        for rule_identity in rule_identities:
            del self._rules[rule_identity]
        return changed or bool(rule_identities)

    def _add_rule(self, item: TableDTO | ChainDTO | RuleDTO) -> bool:
        if not isinstance(item, RuleDTO):
            return False
        identity = _rule_identity(item)
        if self._rules.get(identity) == item:
            return False
        self._rules[identity] = item
        return True

    def _remove_rule(self, item: TableDTO | ChainDTO | RuleDTO) -> bool:
        if not isinstance(item, RuleDTO):
            return False
        return self._rules.pop(_rule_identity(item), None) is not None


def _table_identity(table: TableDTO) -> _TableIdentity:
    return _TableIdentity(table.family, table.name)


def _chain_identity(chain: ChainDTO) -> _ChainIdentity:
    return _ChainIdentity(chain.family, chain.table, chain.name)


def _rule_identity(rule: RuleDTO) -> _RuleIdentity:
    return _RuleIdentity(rule.family, rule.table, rule.chain, rule.handle)
