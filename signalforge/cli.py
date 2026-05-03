from __future__ import annotations

import argparse
from pathlib import Path

from signalforge.generators.graph_gen import generate_dot
from signalforge.generators.markdown_gen import generate_markdown
from signalforge.generators.python_gen import generate_python
from signalforge.generators.report_gen import generate_report
from signalforge.generators.rust_gen import generate_rust
from signalforge.parser import SchemaParseError, load_schema
from signalforge.validator import validate_schema


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="signalforge",
        description="Generate code, docs, graphs, and reports from component message schemas.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a schema file.")
    validate_parser.add_argument("schema")

    generate_parser = subparsers.add_parser("generate", help="Generate Python and Rust code.")
    generate_parser.add_argument("schema")
    generate_parser.add_argument("--out", required=True)

    graph_parser = subparsers.add_parser("graph", help="Generate a Graphviz DOT communication graph.")
    graph_parser.add_argument("schema")
    graph_parser.add_argument("--out", required=True)

    docs_parser = subparsers.add_parser("docs", help="Generate Markdown interface documentation.")
    docs_parser.add_argument("schema")
    docs_parser.add_argument("--out", required=True)

    all_parser = subparsers.add_parser("all", help="Generate all outputs in one directory.")
    all_parser.add_argument("schema")
    all_parser.add_argument("--out", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        schema = load_schema(args.schema)
    except SchemaParseError as exc:
        print(str(exc))
        return 2

    validation = validate_schema(schema)

    if args.command == "validate":
        return handle_validate(schema_path=args.schema, validation=validation)
    if args.command == "generate":
        return handle_generate(schema, validation, Path(args.out))
    if args.command == "graph":
        return handle_graph(schema, validation, Path(args.out))
    if args.command == "docs":
        return handle_docs(schema, validation, Path(args.out))
    if args.command == "all":
        return handle_all(schema, validation, Path(args.schema), Path(args.out))

    parser.error("Unknown command.")
    return 2


def handle_validate(*, schema_path: str, validation) -> int:
    if validation.valid:
        print(f"Schema is valid: {schema_path}")
        return 0

    print("Schema is invalid:")
    for issue in validation.errors:
        print(f"- {issue.path}: {issue.message}")
    return 1


def handle_generate(schema, validation, out_dir: Path) -> int:
    if not validation.valid:
        return handle_validate(schema_path=str(schema.source_path or ""), validation=validation)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "interfaces.py").write_text(generate_python(schema), encoding="utf-8")
    (out_dir / "interfaces.rs").write_text(generate_rust(schema), encoding="utf-8")
    print(f"Generated Python and Rust code in {out_dir}")
    return 0


def handle_graph(schema, validation, out_path: Path) -> int:
    if not validation.valid:
        return handle_validate(schema_path=str(schema.source_path or ""), validation=validation)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(generate_dot(schema), encoding="utf-8")
    print(f"Generated graph at {out_path}")
    return 0


def handle_docs(schema, validation, out_path: Path) -> int:
    if not validation.valid:
        return handle_validate(schema_path=str(schema.source_path or ""), validation=validation)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(generate_markdown(schema), encoding="utf-8")
    print(f"Generated documentation at {out_path}")
    return 0


def handle_all(schema, validation, schema_path: Path, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_text = generate_report(schema, validation, schema_path)
    (out_dir / "validation_report.json").write_text(report_text, encoding="utf-8")

    if not validation.valid:
        print(f"Validation report written to {out_dir / 'validation_report.json'}")
        return handle_validate(schema_path=str(schema_path), validation=validation)

    (out_dir / "interfaces.py").write_text(generate_python(schema), encoding="utf-8")
    (out_dir / "interfaces.rs").write_text(generate_rust(schema), encoding="utf-8")
    (out_dir / "interfaces.md").write_text(generate_markdown(schema), encoding="utf-8")
    (out_dir / "interfaces.dot").write_text(generate_dot(schema), encoding="utf-8")
    print(f"Generated all outputs in {out_dir}")
    return 0
