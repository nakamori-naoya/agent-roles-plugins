#!/usr/bin/env bash
# Scenario: agent-rolesが役割のCatalogを検査済みで両runtimeへ配布できる。
set -uo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# 保守toolの実装元は兄弟checkoutの harness-tools。無ければ止まる（fixtureで代用しない）。
TOOLS="$ROOT/../harness-tools/tools"
[ -d "$TOOLS" ] || { echo "[error] 兄弟 checkout harness-tools が無い: $TOOLS" >&2; exit 2; }
PLUGIN="$ROOT/plugins/agent-roles"
failed=0
skill_frontmatter_name() {
  awk 'NR==1 { if ($0 != "---") exit 2; next } $0=="---" { found=1; exit } { print } END { if (!found) exit 2 }' "$1" \
    | yq -er '.name | select(tag == "!!str" and length > 0)' -
}
python3 "$TOOLS/test-hardening.py" --repository "$ROOT" || failed=1
python3 -m unittest discover -s "$ROOT/tests" -p test_catalog_contract.py || failed=1


python3 "$TOOLS/validate-plugin-repository.py" "$ROOT" || failed=1
python3 "$TOOLS/validate-plugin-repository.py" --self-test || failed=1

for manifest in "$PLUGIN/.codex-plugin/plugin.json" "$PLUGIN/.claude-plugin/plugin.json"; do
  jq -e '.name=="agent-roles" and (.version|test("^[0-9]+[.][0-9]+[.][0-9]+"))' "$manifest" >/dev/null || failed=1
done
jq -e '.name=="agent-roles" and (.plugins|length==1) and .plugins[0].name=="agent-roles" and (.plugins[0].version|test("^[0-9]+[.][0-9]+[.][0-9]+"))' \
  "$ROOT/.agents/plugins/marketplace.json" "$ROOT/.claude-plugin/marketplace.json" >/dev/null || failed=1

python3 "$PLUGIN/scripts/validate_catalog.py" "$PLUGIN/roles/catalog.yml" >/dev/null || failed=1
TMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/agent-roles-validation.XXXXXX") || exit 2
trap 'rm -rf "$TMP_ROOT"' EXIT
printf '%s\n' '---' "name: 'fixture-skill' # comment" '---' 'name: body-only' > "$TMP_ROOT/frontmatter-valid.md"
printf '%s\n' '---' 'description: no name' '---' 'name: body-only' > "$TMP_ROOT/frontmatter-invalid.md"
[ "$(skill_frontmatter_name "$TMP_ROOT/frontmatter-valid.md")" = "fixture-skill" ] \
  && ! skill_frontmatter_name "$TMP_ROOT/frontmatter-invalid.md" >/dev/null 2>&1 || failed=1
python3 "$PLUGIN/scripts/export_catalog.py" --target "$TMP_ROOT/builtin@2.json" >/dev/null || failed=1
jq -e '.apiVersion=="roles.harness/v1" and .metadata.name=="builtin" and .metadata.version==2' \
  "$TMP_ROOT/builtin@2.json" >/dev/null || failed=1
[ "$(skill_frontmatter_name "$PLUGIN/skills/assign-agent-roles/SKILL.md")" = "assign-agent-roles" ] || failed=1

if [ "$failed" -eq 0 ]; then
  echo 'Validation: passed'
else
  echo 'Validation: failed'
fi
[ "$failed" -eq 0 ]
