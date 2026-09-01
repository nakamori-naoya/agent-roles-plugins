---
name: assign-agent-roles
description: 複数agentへmanager、advisor、worker、reviewer、researcherの役割を割り当て、成果物・権限・受け渡し・越境禁止を定める。agent fleetの起動やpane操作は行わない。
---

# assign-agent-roles

役割は作業手順ではなく、産出する成果物の型で分ける。

## Catalogを検査する

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-/absolute/path/to/agent-roles}"
python3 "${PLUGIN_ROOT}/scripts/validate_catalog.py" "${PLUGIN_ROOT}/roles/catalog.yml" --output-json
```

検査が失敗したcatalogを使わない。既定の静的方針は`config/defaults.yml`、roleと関係の正本は`roles/catalog.yml`にある。

## 必要なroleだけを割り当てる

- managerは目的、完了条件、停止条件と最終判断を持つ。
- advisorは選択肢とトレードオフを返し、合否を判定しない。
- workerは成果物と検証結果を返し、自分の成果物を評価済みにしない。
- reviewerは作業経緯から独立して再現可能な反証を返し、修正しない。
- researcherは出典と時点のある事実を返し、推奨しない。

全roleを常に立てる必要はない。ただし必要なroleの担い手がいないとき、別roleへ暗黙に兼任させない。advisorが助言した成果物を同じadvisorにreviewさせず、workerに自分の成果物をreviewさせない。

## Fleetとの境界

このpluginが返すのはrole definitionとassignmentである。agent instance、model、task、Herdr pane、runtime binding、UI layoutはFleet側の関心なので、role catalogへ書き足さない。

## 報告する

- 割り当てるroleと、割り当てないrole
- roleごとの目的、完了条件、停止条件、期待する成果物
- 許可された受け渡し経路
- reviewer不在など未検証になる範囲
