#!/usr/bin/env python3
"""Validate the agent-roles YAML catalog without accepting unknown structure."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_yaml(path: Path) -> dict:
    try:
        result = subprocess.run(
            ["yq", "-o=json", "-I=0", ".", str(path)],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ValueError("yq command is required to read YAML") from exc
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "invalid YAML")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"yq returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("catalog root must be a mapping")
    return value


def require_keys(value: dict, allowed: set[str], required: set[str], where: str) -> None:
    missing = sorted(required - value.keys())
    unknown = sorted(value.keys() - allowed)
    if missing:
        raise ValueError(f"{where}: missing keys: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"{where}: unknown keys: {', '.join(unknown)}")


def validate(catalog: dict) -> dict:
    require_keys(catalog, {"apiVersion", "kind", "metadata", "spec"}, {"apiVersion", "kind", "metadata", "spec"}, "catalog")
    if catalog["apiVersion"] != "roles.harness/v1" or catalog["kind"] != "RoleCatalog":
        raise ValueError("catalog: unsupported apiVersion or kind")
    metadata = catalog["metadata"]
    spec = catalog["spec"]
    if not isinstance(metadata, dict) or not isinstance(spec, dict):
        raise ValueError("metadata and spec must be mappings")
    require_keys(metadata, {"name", "version"}, {"name", "version"}, "metadata")
    require_keys(spec, {"artifactTypes", "roles", "relations", "exchange", "isolation"}, {"artifactTypes", "roles", "relations", "exchange", "isolation"}, "spec")

    artifact_types = spec["artifactTypes"]
    roles = spec["roles"]
    relations = spec["relations"]
    if not isinstance(artifact_types, list) or not artifact_types or len(set(artifact_types)) != len(artifact_types):
        raise ValueError("spec.artifactTypes must be a non-empty unique list")
    if not isinstance(roles, list) or not roles:
        raise ValueError("spec.roles must be a non-empty list")

    role_keys = {"id", "produces", "mission", "responsibilities", "forbidden", "authority", "receives", "sends"}
    role_ids: list[str] = []
    for index, role in enumerate(roles):
        if not isinstance(role, dict):
            raise ValueError(f"spec.roles[{index}] must be a mapping")
        require_keys(role, role_keys, role_keys, f"spec.roles[{index}]")
        role_id = role["id"]
        if not isinstance(role_id, str) or not role_id:
            raise ValueError(f"spec.roles[{index}].id must be a non-empty string")
        role_ids.append(role_id)
        for key in ("responsibilities", "forbidden", "authority", "receives", "sends"):
            if not isinstance(role[key], list):
                raise ValueError(f"role {role_id}.{key} must be a list")
        for key in ("receives", "sends"):
            unknown = sorted(set(role[key]) - set(artifact_types))
            if unknown:
                raise ValueError(f"role {role_id}.{key} has unknown artifact types: {', '.join(unknown)}")
    if len(set(role_ids)) != len(role_ids):
        raise ValueError("role ids must be unique")

    if not isinstance(relations, list):
        raise ValueError("spec.relations must be a list")
    role_set = set(role_ids)
    for index, relation in enumerate(relations):
        if not isinstance(relation, dict):
            raise ValueError(f"spec.relations[{index}] must be a mapping")
        require_keys(relation, {"from", "to", "permits", "sends"}, {"from", "to", "permits", "sends"}, f"spec.relations[{index}]")
        if relation["from"] not in role_set or relation["to"] not in role_set:
            raise ValueError(f"spec.relations[{index}] references an unknown role")
        if not isinstance(relation["permits"], list) or not isinstance(relation["sends"], list):
            raise ValueError(f"spec.relations[{index}] permits and sends must be lists")
        unknown = sorted(set(relation["sends"]) - set(artifact_types))
        if unknown:
            raise ValueError(f"spec.relations[{index}] has unknown artifact types: {', '.join(unknown)}")
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--output-json", action="store_true")
    args = parser.parse_args()
    try:
        catalog = validate(load_yaml(args.catalog))
    except ValueError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2
    if args.output_json:
        print(json.dumps(catalog, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
    else:
        print("Role catalog: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
