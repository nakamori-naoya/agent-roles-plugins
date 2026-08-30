---
name: assign-agent-roles
description: 複数agentへ成果物の型に基づく役割と受け渡し境界を割り当てる。agentの起動やpane操作は行わない。
---

# assign-agent-roles

このentryは配布形式を中立化する薄い入口である。plugin rootを検証し、root直下の正本`SKILL.md`を全文読んで従う。

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-/absolute/path/to/agent-roles}"
test -f "${PLUGIN_ROOT}/SKILL.md" || exit 2
cat "${PLUGIN_ROOT}/SKILL.md"
```
