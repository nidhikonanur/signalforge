from __future__ import annotations

from pathlib import Path

from signalforge.generators.graph_gen import generate_dot
from signalforge.parser import load_schema


def test_dot_graph_generation_includes_expected_edge() -> None:
    schema = load_schema(Path(__file__).resolve().parents[1] / "examples" / "sample_schema.yaml")
    generated = generate_dot(schema)
    assert '"BatteryController" -> "TelemetryService" [label="BatteryStatus"];' in generated
    assert '"ThermalManager" -> "BatteryController" [label="ThermalCommand"];' in generated
