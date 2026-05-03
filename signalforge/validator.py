from __future__ import annotations

from collections import Counter

from signalforge.models import (
    ALLOWED_DIRECTIONS,
    ALLOWED_FIELD_TYPES,
    InterfaceSchema,
    ValidationIssue,
    ValidationResult,
)


def validate_schema(schema: InterfaceSchema) -> ValidationResult:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    component_names = [component.name for component in schema.components]
    for name, count in Counter(component_names).items():
        if count > 1:
            errors.append(ValidationIssue(path="components", message=f"Duplicate component name '{name}' found."))

    message_ids: dict[int, str] = {}
    message_names: dict[str, tuple[str, str, tuple[tuple[str, str], ...]]] = {}

    for component_index, component in enumerate(schema.components):
        component_path = f"components[{component_index}]"

        if not component.name:
            errors.append(ValidationIssue(path=f"{component_path}.name", message="Component name is required."))

        for message_index, message in enumerate(component.messages):
            message_path = f"{component_path}.messages[{message_index}]"

            if message.id is None:
                errors.append(ValidationIssue(path=f"{message_path}.id", message="Message id is required."))
            elif not isinstance(message.id, int):
                errors.append(ValidationIssue(path=f"{message_path}.id", message="Message id must be an integer."))
            elif message.id in message_ids:
                errors.append(
                    ValidationIssue(
                        path=f"{message_path}.id",
                        message=f"Duplicate message id '{message.id}' also used by {message_ids[message.id]}.",
                    )
                )
            else:
                message_ids[message.id] = f"{component.name}.{message.name}"

            field_signature = tuple((field.name, field.type) for field in message.fields)

            if not message.name:
                errors.append(ValidationIssue(path=f"{message_path}.name", message="Message name is required."))
            else:
                previous_message = message_names.get(message.name)
                if previous_message is None:
                    message_names[message.name] = (component.name, message.direction, field_signature)
                else:
                    previous_component, previous_direction, previous_signature = previous_message
                    if previous_direction == message.direction:
                        errors.append(
                            ValidationIssue(
                                path=f"{message_path}.name",
                                message=(
                                    f"Duplicate message name '{message.name}' used by both "
                                    f"{previous_component} and {component.name} with direction '{message.direction}'."
                                ),
                            )
                        )
                    elif previous_signature != field_signature:
                        errors.append(
                            ValidationIssue(
                                path=f"{message_path}.fields",
                                message=(
                                    f"Message '{message.name}' is reused across components but field definitions do not match."
                                ),
                            )
                        )

            if not message.direction:
                errors.append(
                    ValidationIssue(path=f"{message_path}.direction", message="Message direction is required.")
                )
            elif message.direction not in ALLOWED_DIRECTIONS:
                errors.append(
                    ValidationIssue(
                        path=f"{message_path}.direction",
                        message=(
                            f"Unsupported direction '{message.direction}'. "
                            f"Allowed values: {', '.join(sorted(ALLOWED_DIRECTIONS))}."
                        ),
                    )
                )

            if message.frequency_hz is not None:
                if not isinstance(message.frequency_hz, (int, float)):
                    errors.append(
                        ValidationIssue(
                            path=f"{message_path}.frequency_hz",
                            message="Frequency must be a number when provided.",
                        )
                    )
                elif message.frequency_hz <= 0:
                    errors.append(
                        ValidationIssue(
                            path=f"{message_path}.frequency_hz",
                            message="Frequency must be positive when provided.",
                        )
                    )

            if not message.fields:
                errors.append(ValidationIssue(path=f"{message_path}.fields", message="Message fields are required."))

            field_names: set[str] = set()
            for field_index, field in enumerate(message.fields):
                field_path = f"{message_path}.fields[{field_index}]"

                if not field.name:
                    errors.append(ValidationIssue(path=f"{field_path}.name", message="Field name is required."))
                elif field.name in field_names:
                    errors.append(
                        ValidationIssue(
                            path=f"{field_path}.name",
                            message=f"Duplicate field name '{field.name}' in message '{message.name}'.",
                        )
                    )
                else:
                    field_names.add(field.name)

                if not field.type:
                    errors.append(ValidationIssue(path=f"{field_path}.type", message="Field type is required."))
                elif field.type not in ALLOWED_FIELD_TYPES:
                    errors.append(
                        ValidationIssue(
                            path=f"{field_path}.type",
                            message=(
                                f"Unsupported field type '{field.type}'. "
                                f"Allowed values: {', '.join(sorted(ALLOWED_FIELD_TYPES))}."
                            ),
                        )
                    )

        if not component.messages:
            warnings.append(
                ValidationIssue(path=f"{component_path}.messages", message="Component has no messages defined.")
            )

    return ValidationResult(valid=not errors, errors=errors, warnings=warnings)
