# Agent Roles Plugins

複数agentへ役割を割り当てるClaude Code/Codex両対応marketplaceである。旧`agent-roles`のmanager、advisor、worker、reviewer、researcherを移植し、role definitionとrole間の関係をYAML catalogとして検査可能にした。

このpluginはrole assignmentだけを扱う。agent instance、task、model、Herdr pane、runtime binding、UI layoutはFleet pluginの責務である。

## 公開する役割Catalog

役割の目的、責務、禁止事項、権限、受け渡し関係の正本は`roles/catalog.yml`だけである。他pluginへ内部配置を探索させず、検査済みの版固定JSONを公開成果物として書き出す。

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/export_catalog.py" \
  --target "$HOME/.config/agent-roles/catalogs/builtin@1.json"
```

Fleetなどの利用側は、この明示的に書き出したJSONを入力として受け取る。利用側が役割名や役割本文を複製してはならない。Catalogの書き出しはagent instanceの作成、タスク割当、Fleet起動を行わない。

役割を選ぶ基準、兼任禁止、成果報告から受容までの業務ルールとBDDは、[エージェント役割割当の業務知識と振る舞い](docs/2026-09-02-エージェント役割割当-業務知識と振る舞い.md)を正本とする。

## 検証

```bash
bash scripts/validate.sh
```
エージェントごとの役割・責務・関係性を定義するプラグイン marketplace
