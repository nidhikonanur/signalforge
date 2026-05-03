from __future__ import annotations

from pathlib import Path

from signalforge.generators.rust_gen import generate_rust
from signalforge.parser import load_schema


def test_rust_code_generation_includes_expected_struct() -> None:
    schema = load_schema(Path(__file__).resolve().parents[1] / "examples" / "sample_schema.yaml")
    generated = generate_rust(schema)
    assert "pub enum MessageDirection" in generated
    assert "pub struct BatteryStatus" in generated
    assert "pub pack_voltage: f32" in generated
