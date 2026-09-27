#!/usr/bin/env bash
# Scenario: agent-rolesが役割のCatalogを検査済みで両runtimeへ配布できる。
# 配置と manifest は harness-tools の validate-plugin-repository.py が判定する。ここで足すのは Catalog の検査と書き出しである。
set -uo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# 保守toolの実装元は兄弟checkoutの harness-tools。無ければ止まる（fixtureで代用しない）。
TOOLS="$ROOT/../harness-tools/tools"
[ -d "$TOOLS" ] || { echo "[error] 兄弟 checkout harness-tools が無い: $TOOLS" >&2; exit 2; }
PLUGIN="$ROOT/plugins/agent-roles"
failed=0
python3 "$TOOLS/test-hardening.py" --repository "$ROOT" || failed=1
python3 -m unittest discover -s "$ROOT/tests" -p test_catalog_contract.py || failed=1

python3 "$TOOLS/validate-plugin-repository.py" "$ROOT" || failed=1
python3 "$TOOLS/validate-plugin-repository.py" --self-test || failed=1

python3 "$PLUGIN/scripts/validate_catalog.py" "$PLUGIN/roles/catalog.yml" >/dev/null || failed=1
TMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/agent-roles-validation.XXXXXX") || exit 2
trap 'rm -rf "$TMP_ROOT"' EXIT
python3 "$PLUGIN/scripts/export_catalog.py" --target "$TMP_ROOT/builtin@2.json" >/dev/null || failed=1
jq -e '.apiVersion=="roles.harness/v1" and .metadata.name=="builtin" and .metadata.version==2' \
  "$TMP_ROOT/builtin@2.json" >/dev/null || failed=1

if [ "$failed" -eq 0 ]; then
  echo 'Validation: passed'
else
  echo 'Validation: failed'
fi
[ "$failed" -eq 0 ]
