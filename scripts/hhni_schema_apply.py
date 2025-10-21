#!/usr/bin/env python
"""Upload HHNI GraphQL schema to DGraph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests


def apply_schema(dgraph_url: str, schema_path: Path) -> None:
    text = schema_path.read_text(encoding="utf-8")
    payload: dict[str, Any] = {"query": "mutation updateSchema($schema: String!) { updateGQLSchema(input: { set: { schema: $schema }}) { gqlSchema { id } } }", "variables": {"schema": text}}
    endpoint = dgraph_url.rstrip("/") + "/graphql"
    response = requests.post(endpoint, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(json.dumps(data["errors"]))
    print("Schema applied", data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload HHNI schema to DGraph")
    parser.add_argument("--dgraph-url", default="http://localhost:8080", help="DGraph GraphQL endpoint base URL")
    parser.add_argument("--schema", default="schemas/hhni.graphql", help="Path to GraphQL schema file")
    args = parser.parse_args()
    apply_schema(args.dgraph_url, Path(args.schema))


if __name__ == "__main__":
    main()
