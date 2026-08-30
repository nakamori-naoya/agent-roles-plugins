# Agent Roles Plugins

複数agentへ役割を割り当てるClaude Code/Codex両対応marketplaceである。旧`agent-roles`のmanager、advisor、worker、reviewer、researcherを移植し、role definitionとrole間の関係をYAML catalogとして検査可能にした。

このpluginはrole assignmentだけを扱う。agent instance、task、model、Herdr pane、runtime binding、UI layoutはFleet pluginの責務である。

## 検証

```bash
bash scripts/validate.sh
```
エージェントごとの役割・責務・関係性を定義するプラグイン marketplace
