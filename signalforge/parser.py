from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from signalforge.models import Component, Field, InterfaceSchema, Message


class SchemaParseError(ValueError):
    """Raised when raw YAML cannot be converted into a schema shape."""


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    source_path = Path(path)
    try:
        raw = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SchemaParseError(f"Schema file not found: {source_path}") from exc
    except yaml.YAMLError as exc:
        raise SchemaParseError(f"Failed to parse YAML in {source_path}: {exc}") from exc

    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise SchemaParseError(f"Top-level YAML document must be a mapping in {source_path}.")
    return raw


def parse_schema(data: dict[str, Any], source_path: str | Path | None = None) -> InterfaceSchema:
    components_data = data.get("components", [])
    if components_data is None:
        components_data = []
    if not isinstance(components_data, list):
        raise SchemaParseError("'components' must be a list.")

    components: list[Component] = []
    for component_data in components_data:
        if not isinstance(component_data, dict):
            raise SchemaParseError("Each component entry must be a mapping.")

        name = component_data.get("name", "")
        messages_data = component_data.get("messages", []) or []
        if not isinstance(messages_data, list):
            raise SchemaParseError(f"Component '{name or '<unknown>'}' has non-list 'messages'.")

        messages: list[Message] = []
        for message_data in messages_data:
            if not isinstance(message_data, dict):
                raise SchemaParseError(f"Component '{name or '<unknown>'}' contains a non-mapping message.")

            fields_data = message_data.get("fields", []) or []
            if not isinstance(fields_data, list):
                raise SchemaParseError(
                    f"Message '{message_data.get('name', '<unknown>')}' has non-list 'fields'."
                )

            fields = [
                Field(
                    name=str(field_data.get("name", "")),
                    type=str(field_data.get("type", "")),
                    unit=(str(field_data.get("unit")) if field_data.get("unit") is not None else None),
                )
                for field_data in fields_data
                if isinstance(field_data, dict)
            ]

            messages.append(
                Message(
                    id=message_data.get("id"),
                    name=str(message_data.get("name", "")),
                    direction=str(message_data.get("direction", "")),
                    fields=fields,
                    frequency_hz=message_data.get("frequency_hz"),
                )
            )

        components.append(Component(name=str(name), messages=messages))

    return InterfaceSchema(components=components, source_path=Path(source_path) if source_path else None)


def load_schema(path: str | Path) -> InterfaceSchema:
    raw = load_yaml_file(path)
    return parse_schema(raw, source_path=path)
