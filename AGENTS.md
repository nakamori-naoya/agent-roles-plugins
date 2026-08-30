# AGENTS.md

このrepositoryは、複数agentへ成果物の型に基づく役割を割り当てる`agent-roles` marketplaceのsourceである。

- role definition、artifact type、role間の関係はYAMLを正本にする。
- roleとagent instance、task、model、runtime binding、pane layoutを混同しない。
- このpluginはagentを起動せず、Herdrや他runtimeを操作しない。
- advisorとreviewer、workerとreviewerを同じ成果物で兼任させない。
- install cacheは編集せず、このsourceを正本として変更する。
- 変更後は`bash scripts/validate.sh`を実行する。
