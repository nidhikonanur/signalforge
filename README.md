# SignalForge

SignalForge is a developer productivity tool that reads YAML interface schemas and generates strongly typed code, validation output, interface documentation, and a communication graph. It is designed as an original portfolio project inspired by the kind of internal integration tooling teams use to keep component interfaces understandable, enforceable, and easy to evolve.

## Why I Built It

I wanted a project that shows both backend/tooling depth and systems thinking. SignalForge demonstrates Python CLI development, schema validation, code generation, lightweight visualization, and a maintainable architecture built around a single source of truth for component communication definitions.

## What Problem It Solves

When component interfaces are defined informally, teams tend to duplicate message contracts across codebases, docs drift out of date, and communication dependencies become harder to debug. SignalForge treats the schema as the canonical input and generates:

- typed Python message models
- typed Rust message models
- Markdown interface docs
- JSON validation reports
- Graphviz communication graphs

This improves consistency and makes integration problems easier to inspect.

## Features

- YAML schema parsing with actionable validation errors
- Strongly typed Python dataclass generation
- Rust struct and enum generation with simple primitive mappings
- Markdown interface documentation generation
- JSON validation report generation
- Graphviz DOT graph generation for publisher/subscriber relationships
- Fast local CLI with modular subcommands
- Local pytest coverage for validation and generation behavior

## Architecture

- `signalforge/parser.py`: loads YAML and converts it into schema objects
- `signalforge/models.py`: dataclass-based schema and validation models
- `signalforge/validator.py`: enforces naming, typing, and uniqueness rules
- `signalforge/generators/`: separate output modules for Python, Rust, Markdown, DOT, and JSON report generation
- `signalforge/cli.py`: CLI entrypoint and command orchestration

The parser and validator create a single normalized schema model. All generators consume that same model, which keeps the generated code, docs, and graph aligned.

## CLI Usage

Run via module:

```bash
python -m signalforge validate examples/sample_schema.yaml
python -m signalforge generate examples/sample_schema.yaml --out generated/
python -m signalforge graph examples/sample_schema.yaml --out generated/interfaces.dot
python -m signalforge docs examples/sample_schema.yaml --out generated/interfaces.md
python -m signalforge all examples/sample_schema.yaml --out generated/
```

If you install the package locally, you can also run:

```bash
signalforge validate examples/sample_schema.yaml
signalforge all examples/sample_schema.yaml --out generated/
```

## Validation Rules

- Component names must be unique
- Message IDs must be unique globally
- Message names must not be duplicated with the same direction across components
- If a message name is reused across publisher and subscriber components, the field definitions must match
- Field names must be unique within a message
- Required message properties: `id`, `name`, `direction`, `fields`
- Required field properties: `name`, `type`
- Allowed directions: `publish`, `subscribe`, `request`, `response`
- Allowed field types: `uint8`, `uint16`, `uint32`, `int32`, `float32`, `float64`, `bool`, `string`
- Frequencies, when present, must be positive

## Generated Output Examples

### Python

```python
@dataclass(slots=True)
class BatteryStatus:
    pack_voltage: float
    pack_current: float
    state_of_charge: int
```

### Rust

```rust
#[derive(Debug, Clone, PartialEq)]
pub struct BatteryStatus {
    pub pack_voltage: f32,
    pub pack_current: f32,
    pub state_of_charge: u8,
}
```

### DOT Graph

```dot
"BatteryController" -> "TelemetryService" [label="BatteryStatus"];
"ThermalManager" -> "BatteryController" [label="ThermalCommand"];
```

## Setup Instructions

```bash
cd /Users/nidhikonanur/Documents/Playground/signalforge
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Test Instructions

```bash
cd /Users/nidhikonanur/Documents/Playground/signalforge
source .venv/bin/activate
pytest
```

## Limitations

- YAML parsing is intentionally lightweight and not backed by a formal JSON Schema spec
- Generated Rust is designed for readability and integration scaffolding, not a complete runtime protocol library
- The graph only creates edges for `publish` to `subscribe` relationships with matching message names
- Validation warnings are minimal in this first version

## Future Improvements

- Add JSON Schema export
- Add support for nested field types and arrays
- Add richer warnings around unused or orphaned messages
- Add customizable templates for generated code
- Add SVG or PNG graph rendering when Graphviz is installed
- Add incremental generation and formatting hooks
