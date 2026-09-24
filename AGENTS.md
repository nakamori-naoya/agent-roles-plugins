> 作業を始める前に、workspace規約入口 `/Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/AGENTS.md` を読み、そこから指定される共通規約とこのrepository固有の規則を適用する。

# AGENTS.md

このrepositoryは、複数agentへ成果物の型に基づく役割を割り当てる`agent-roles` marketplaceのsourceである。

- role definition、artifact type、role間の関係はYAMLを正式な定義とする。
- marketplaceへ公開するインストール対象は、利用者の役割定義作業を完了させる`agent-roles`だけにする。内部処理を別entryへ分解しない。
- roleとagent instance、task、model、runtime binding、pane layoutを混同しない。
- このpluginはagentを起動せず、Herdrや他runtimeを操作しない。
- advisorとreviewer、workerとreviewerを同じ成果物で兼任させない。
- install cacheは編集せず、このsourceだけを変更する。
- 変更後は`bash scripts/validate.sh`を実行する。

## 検査スクリプトは、意味が一意に決まることだけを判定する

このrepositoryの検査スクリプト（validate、lint、verify、checkなど、名前を問わない）が判定してよいのは、ファイルや見出しの有無、識別子や版の一致、宣言と配置の対応、禁止された書き方の有無のように、入力と基準資料から意味が決定論的に一意に決まることだけである。読んで解釈しないと決まらないことや、件数や語の出現のような品質の代わりの指標は判定せず、エージェントが読んで評価する（意味評価）。判定が一意に決まることを宣言できない検査は作らず、詳しい条件は `/Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/.agents/rules/deterministic-validation.md` に従う。
