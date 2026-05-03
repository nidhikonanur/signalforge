from __future__ import annotations

from pathlib import Path

from signalforge.parser import load_schema
from signalforge.validator import validate_schema


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_valid_schema_passes() -> None:
    schema = load_schema(EXAMPLES / "sample_schema.yaml")
    result = validate_schema(schema)
    assert result.valid is True
    assert result.errors == []


def test_duplicate_message_ids_fail() -> None:
    schema = load_schema(EXAMPLES / "invalid_duplicate_id.yaml")
    result = validate_schema(schema)
    assert result.valid is False
    assert any("Duplicate message id" in issue.message for issue in result.errors)


def test_unsupported_field_type_fails() -> None:
    schema = load_schema(EXAMPLES / "invalid_field_type.yaml")
    result = validate_schema(schema)
    assert result.valid is False
    assert any("Unsupported field type" in issue.message for issue in result.errors)


def test_duplicate_field_names_fail() -> None:
    schema = load_schema(EXAMPLES / "sample_schema.yaml")
    schema.components[0].messages[0].fields.append(schema.components[0].messages[0].fields[0])
    result = validate_schema(schema)
    assert result.valid is False
    assert any("Duplicate field name" in issue.message for issue in result.errors)


def test_missing_required_properties_fail() -> None:
    schema = load_schema(EXAMPLES / "sample_schema.yaml")
    schema.components[0].messages[0].name = ""
    schema.components[0].messages[0].fields = []
    result = validate_schema(schema)
    assert result.valid is False
    assert any("Message name is required" in issue.message for issue in result.errors)
    assert any("Message fields are required" in issue.message for issue in result.errors)
