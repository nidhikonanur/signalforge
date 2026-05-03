from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from signalforge.models import InterfaceSchema, ValidationResult


def generate_report(schema: InterfaceSchema, validation: ValidationResult, schema_path: str | Path) -> str:
    payload = {
        "schema_file_name": Path(schema_path).name,
        "valid": validation.valid,
        "errors": [issue.to_dict() for issue in validation.errors],
        "warnings": [issue.to_dict() for issue in validation.warnings],
        "component_count": schema.component_count,
        "message_count": schema.message_count,
        "field_count": schema.field_count,
        "generated_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload, indent=2) + "\n"
