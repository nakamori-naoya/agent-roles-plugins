#!/usr/bin/env bash
# Scenario: agent-rolesがYAML catalogを正本として両runtimeへ配布できる。
set -uo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PLUGIN="$ROOT/plugins/agent-roles"
failed=0

for manifest in "$PLUGIN/.codex-plugin/plugin.json" "$PLUGIN/.claude-plugin/plugin.json"; do
  jq -e '.name=="agent-roles" and .version=="0.1.1"' "$manifest" >/dev/null || failed=1
done
jq -e '.name=="agent-roles" and (.plugins|length==1) and .plugins[0].name=="agent-roles" and .plugins[0].version=="0.1.1"' \
  "$ROOT/.agents/plugins/marketplace.json" "$ROOT/.claude-plugin/marketplace.json" >/dev/null || failed=1

python3 "$PLUGIN/scripts/validate_catalog.py" "$PLUGIN/roles/catalog.yml" >/dev/null || failed=1
TMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/agent-roles-validation.XXXXXX") || exit 2
trap 'rm -rf "$TMP_ROOT"' EXIT
python3 "$PLUGIN/scripts/export_catalog.py" --target "$TMP_ROOT/builtin@1.json" >/dev/null || failed=1
jq -e '.apiVersion=="roles.harness/v1" and .metadata.name=="builtin" and .metadata.version==1' \
  "$TMP_ROOT/builtin@1.json" >/dev/null || failed=1
rg -n '^name: assign-agent-roles$' "$PLUGIN/SKILL.md" "$PLUGIN/skills/assign-agent-roles/SKILL.md" >/dev/null || failed=1

if [ "$failed" -eq 0 ]; then
  echo 'Validation: passed'
else
  echo 'Validation: failed'
fi
[ "$failed" -eq 0 ]
