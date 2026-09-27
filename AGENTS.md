> 共通の規約は /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/AGENTS.md にある。ここには、この repository だけの規則を置く。

# AGENTS.md

このrepositoryは、複数agentへ成果物の型に基づく役割を割り当てる`agent-roles` marketplaceのsourceである。

- 役割ごとの成果物、権限、受け渡し、してはいけないことは `plugins/agent-roles/roles/catalog.yml` だけが持つ。SKILL.md は役割を当てはめるときの判断だけを持ち、役割の定義を文章で書き直さない。
- marketplaceへ公開するインストール対象は`agent-roles`だけにし、内部処理を別entryへ分解しない。
