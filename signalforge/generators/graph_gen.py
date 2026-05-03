from __future__ import annotations

from signalforge.models import InterfaceSchema


def generate_dot(schema: InterfaceSchema) -> str:
    publishers: dict[str, list[str]] = {}
    subscribers: dict[str, list[str]] = {}

    for component in schema.components:
        for message in component.messages:
            if message.direction == "publish":
                publishers.setdefault(message.name, []).append(component.name)
            elif message.direction == "subscribe":
                subscribers.setdefault(message.name, []).append(component.name)

    lines = [
        "digraph SignalForgeInterfaces {",
        "    rankdir=LR;",
        '    node [shape=box, style=rounded];',
    ]

    for component in schema.components:
        lines.append(f'    "{component.name}";')

    for message_name, source_components in publishers.items():
        target_components = subscribers.get(message_name, [])
        for source in source_components:
            for target in target_components:
                lines.append(f'    "{source}" -> "{target}" [label="{message_name}"];')

    lines.append("}")
    return "\n".join(lines) + "\n"
