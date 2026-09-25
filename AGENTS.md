> 共通の規約は /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/AGENTS.md にある。ここには、この repository だけの規則を置く。

# AGENTS.md

このrepositoryは、複数agentへ成果物の型に基づく役割を割り当てる`agent-roles` marketplaceのsourceである。

- role definition、artifact type、role間の関係はYAMLを正式な定義とする。
- marketplaceへ公開するインストール対象は、利用者の役割定義作業を完了させる`agent-roles`だけにする。内部処理を別entryへ分解しない。
- roleとagent instance、task、model、runtime binding、pane layoutを混同しない。
- このpluginはagentを起動せず、Herdrや他runtimeを操作しない。
- advisorとreviewer、workerとreviewerを同じ成果物で兼任させない。
