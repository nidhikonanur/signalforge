from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ALLOWED_DIRECTIONS = {"publish", "subscribe", "request", "response"}
ALLOWED_FIELD_TYPES = {
    "uint8",
    "uint16",
    "uint32",
    "int32",
    "float32",
    "float64",
    "bool",
    "string",
}


@dataclass(slots=True)
class Field:
    name: str
    type: str
    unit: str | None = None


@dataclass(slots=True)
class Message:
    id: int
    name: str
    direction: str
    fields: list[Field]
    frequency_hz: float | None = None


@dataclass(slots=True)
class Component:
    name: str
    messages: list[Message] = field(default_factory=list)


@dataclass(slots=True)
class InterfaceSchema:
    components: list[Component]
    source_path: Path | None = None

    @property
    def component_count(self) -> int:
        return len(self.components)

    @property
    def message_count(self) -> int:
        return sum(len(component.messages) for component in self.components)

    @property
    def field_count(self) -> int:
        return sum(len(message.fields) for component in self.components for message in component.messages)


@dataclass(slots=True)
class ValidationIssue:
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "message": self.message}


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    def raise_for_errors(self) -> None:
        if self.valid:
            return
        error_lines = [f"{issue.path}: {issue.message}" for issue in self.errors]
        raise ValueError("Schema validation failed:\n" + "\n".join(error_lines))


JsonObject = dict[str, Any]
