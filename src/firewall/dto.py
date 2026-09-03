from dataclasses import dataclass


@dataclass(frozen=True)
class TableDTO:
    family: str
    name: str


@dataclass(frozen=True)
class ChainDTO:
    family: str
    table: str
    name: str
    hook: str | None
    priority: int | None
    policy: str | None
    chain_type: str | None


@dataclass(frozen=True)
class ExpressionAttributeDTO:
    attribute_type: int
    nested: bool
    network_byte_order: bool
    value: bytes | tuple["ExpressionAttributeDTO", ...]


@dataclass(frozen=True)
class ExpressionDTO:
    name: str
    attributes: tuple[ExpressionAttributeDTO, ...]


@dataclass(frozen=True)
class MetaExpressionDTO:
    key: str
    destination_register: int | None
    source_register: int | None


@dataclass(frozen=True)
class ComparisonExpressionDTO:
    source_register: int
    operation: str
    data: bytes | str
    data_type: str


@dataclass(frozen=True)
class CounterExpressionDTO:
    packets: int
    bytes: int


@dataclass(frozen=True)
class ImmediateExpressionDTO:
    destination_register: int
    data: bytes


@dataclass(frozen=True)
class VerdictExpressionDTO:
    action: str
    chain: str | None
    chain_id: int | None


RuleExpressionDTO = (
    ExpressionDTO
    | MetaExpressionDTO
    | ComparisonExpressionDTO
    | CounterExpressionDTO
    | ImmediateExpressionDTO
    | VerdictExpressionDTO
)


@dataclass(frozen=True)
class RuleDTO:
    family: str
    table: str
    chain: str
    handle: int | None
    expressions: tuple[RuleExpressionDTO, ...]
