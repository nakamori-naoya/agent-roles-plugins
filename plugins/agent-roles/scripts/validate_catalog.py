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


def require_keys(value, allowed, required, where):
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise ValueError(f"{where}: must be a mapping with string keys")
    missing = sorted(required - value.keys())
    unknown = sorted(value.keys() - allowed)
    if missing or unknown:
        raise ValueError(f"{where}: missing={missing}, unknown={unknown}")


def string(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: must be a non-empty string")
    return value


def positive(value, where):
    if type(value) is not int or value < 1:
        raise ValueError(f"{where}: must be a positive integer")


def strings(value, where, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError(f"{where}: must be a list")
    for item in value:
        string(item, where)
    if len(set(value)) != len(value):
        raise ValueError(f"{where}: duplicates are forbidden")
    return set(value)


def subset(value, allowed, where, nonempty=False):
    actual = strings(value, where, nonempty)
    if actual - allowed:
        raise ValueError(f"{where}: unsupported values {sorted(actual - allowed)}")
    return actual


def validate(catalog):
    require_keys(catalog, {"apiVersion", "kind", "metadata", "spec"}, {"apiVersion", "kind", "metadata", "spec"}, "catalog")
    if catalog["apiVersion"] != "roles.harness/v1" or catalog["kind"] != "RoleCatalog":
        raise ValueError("catalog: unsupported apiVersion or kind")
    metadata, spec = catalog["metadata"], catalog["spec"]
    require_keys(metadata, {"name", "version"}, {"name", "version"}, "metadata")
    string(metadata["name"], "metadata.name")
    positive(metadata["version"], "metadata.version")
    keys = {"artifactTypes", "roles", "relations", "exchange", "isolation"}
    require_keys(spec, keys, keys, "spec")
    artifacts = strings(spec["artifactTypes"], "artifactTypes", True)
    if not isinstance(spec["roles"], list) or not spec["roles"]:
        raise ValueError("roles: must be a non-empty list")
    authorities = {"assign", "end_assignment", "accept", "reject", "consult", "work", "stop_self", "block_acceptance", "research"}
    products = {"decision", "opinion", "artifact", "refutation", "fact"}
    roles = {}
    keys = {"id", "version", "produces", "mission", "responsibilities", "forbidden", "authority", "receives", "sends"}
    for role in spec["roles"]:
        require_keys(role, keys, keys, "role")
        role_id = string(role["id"], "role.id")
        if role_id in roles:
            raise ValueError("role ids must be unique")
        positive(role["version"], "role.version")
        if string(role["produces"], "role.produces") not in products:
            raise ValueError("role.produces: unsupported product")
        string(role["mission"], "role.mission")
        strings(role["responsibilities"], "role.responsibilities", True)
        strings(role["forbidden"], "role.forbidden", True)
        subset(role["authority"], authorities, "role.authority")
        subset(role["receives"], artifacts, "role.receives")
        subset(role["sends"], artifacts, "role.sends")
        roles[role_id] = role
    if not isinstance(spec["relations"], list):
        raise ValueError("relations: must be a list")
    seen = set()
    for relation in spec["relations"]:
        keys = {"from", "to", "permits", "sends"}
        require_keys(relation, keys, keys, "relation")
        sender, receiver = string(relation["from"], "relation.from"), string(relation["to"], "relation.to")
        if sender not in roles or receiver not in roles or sender == receiver:
            raise ValueError("relation: unknown or self role reference")
        if (sender, receiver) in seen:
            raise ValueError("relation: duplicate endpoints")
        seen.add((sender, receiver))
        subset(relation["permits"], set(roles[sender]["authority"]), "relation.permits")
        subset(relation["sends"], set(roles[sender]["sends"]) & set(roles[receiver]["receives"]), "relation.sends")
    exchange = spec["exchange"]
    keys = {"maxRounds", "unresolved", "blockedAcceptanceRequires", "duplicates"}
    require_keys(exchange, keys, keys, "exchange")
    positive(exchange["maxRounds"], "exchange.maxRounds")
    if exchange["unresolved"] != "escalate":
        raise ValueError("exchange.unresolved must be escalate")
    subset(exchange["blockedAcceptanceRequires"], {"rework", "human_decision"}, "exchange.blockedAcceptanceRequires", True)
    duplicate = exchange["duplicates"]
    require_keys(duplicate, {"assignment", "report"}, {"assignment", "report"}, "exchange.duplicates")
    if duplicate["assignment"] != "preserve_existing_until_end" or duplicate["report"] != "preserve_existing_unless_content_changed":
        raise ValueError("exchange.duplicates: unsupported policy")
    isolation = spec["isolation"]
    keys = {"advisorCannotReviewOwnAdvice", "workerCannotReviewOwnArtifact"}
    require_keys(isolation, keys, keys, "isolation")
    if any(isolation[key] is not True for key in keys):
        raise ValueError("isolation: separation rules must be true")
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
