#!/usr/bin/env python3
"""Export the validated built-in Role Catalog as a stable JSON artifact."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from validate_catalog import load_yaml, validate


def export_catalog(source: Path, target: Path, *, replace: bool = False) -> dict:
    catalog = validate(load_yaml(source))
    payload = (
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if target.is_symlink():
        raise ValueError("target must not be a symbolic link")
    if target.exists():
        if target.read_bytes() == payload:
            return {"status": "unchanged", "target": str(target)}
        if not replace:
            raise ValueError("target already exists with different content; use --replace")
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return {"status": "exported", "target": str(target)}


def main() -> int:
    parser = argparse.ArgumentParser(prog="export-role-catalog")
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / "roles" / "catalog.yml"
    try:
        result = export_catalog(source, args.target.expanduser(), replace=args.replace)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
