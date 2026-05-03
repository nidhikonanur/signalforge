from __future__ import annotations

from pathlib import Path

from signalforge.generators.python_gen import generate_python
from signalforge.parser import load_schema


def test_python_code_generation_includes_expected_dataclass() -> None:
    schema = load_schema(Path(__file__).resolve().parents[1] / "examples" / "sample_schema.yaml")
    generated = generate_python(schema)
    assert "@dataclass(slots=True)" in generated
    assert "class BatteryStatus:" in generated
    assert "pack_voltage: float" in generated
