# Agent Roles Plugins

複数agentへ役割を割り当てるClaude Code/Codex両対応marketplaceである。旧`agent-roles`のmanager、advisor、worker、reviewer、researcherを移植し、role definitionとrole間の関係をYAML catalogとして検査可能にした。

このpluginはrole assignmentだけを扱う。agent instance、task、model、Herdr pane、runtime binding、UI layoutはFleet pluginの責務である。

## こんなときに使う

**複数のAIエージェントへ、成果物に対する責任と禁止事項を一貫して与えたいときに使う。** 役割名だけでなく、何を担当し、誰へ渡し、何を兼任してはいけないかを検査可能なCatalogとして管理する。

- managerが全体を監視し、workerへ作業を割り当てる責務を揃えたい
- 共有のbase branchへの統合をmanagerだけに許し、workerには完了報告で止まらせたい
- advisorとreviewerを分け、助言した本人が最終判定しないようにしたい
- 複数の艦隊で同じ役割定義を再利用したい
- Hookへ渡す役割文脈を、会話ごとの手書きpromptから切り離したい

このpluginはエージェントを起動しない。task、model、pane配置も決めない。それらを動かす場合は`agent-fleet`と組み合わせる。

## 最初の使い方

1. 同梱Catalogを検査する。
2. 検査済みCatalogを利用者領域へ書き出す。
3. Fleet Specなどの利用側から`role_ref`で参照する。

たとえば、次のように依頼できる。

```text
この成果物を作るworker、助言するadvisor、独立して確認するreviewerの役割境界を検査して。
```

```text
検査済みRole Catalogを書き出し、Fleet Specから参照できる状態にして。
```

## インストール

インストールするのは`agent-roles@agent-roles`です。外部プラグインの追加は不要です。

内部のスキルは同梱されています。個別にインストールせず、公開入口から利用してください。

### Codex

利用するCodexと同じ設定環境で実行してください。

```bash
codex plugin marketplace add nakamori-naoya/agent-roles-plugins
codex plugin add agent-roles@agent-roles
codex plugin list
```

一覧で導入先を確認し、新しい会話で利用してください。

### Claude Code

次は自分の全プロジェクトで使う例です。このプロジェクトのチームで共有する場合は`project`、このプロジェクトで自分だけが使う場合は`local`に変更し、利用先のディレクトリで実行してください。

```bash
CLAUDE_PLUGIN_SCOPE=user
claude plugin marketplace add nakamori-naoya/agent-roles-plugins --scope "$CLAUDE_PLUGIN_SCOPE"
claude plugin install agent-roles@agent-roles --scope "$CLAUDE_PLUGIN_SCOPE"
claude plugin list
```

一覧で導入を確認し、Claude Codeを再起動してください。すでに導入しているパッケージは、次の更新手順を使ってください。

## 更新する

GitHubから登録したmarketplaceを更新し、その公開パッケージを更新します。新規インストールと同じCodexの設定環境、Claude Codeの適用範囲を使ってください。

### Codex

```bash
codex plugin marketplace upgrade agent-roles
codex plugin add agent-roles@agent-roles
codex plugin list
```

更新後は新しい会話で確認してください。ローカルのパスからmarketplaceを登録した場合は、Git版の更新コマンドではなく、その登録先のソースを更新してから追加し直します。

### Claude Code

```bash
# インストール時に合わせてuser / project / localを選ぶ
CLAUDE_PLUGIN_SCOPE=user
claude plugin marketplace update agent-roles
claude plugin update agent-roles@agent-roles --scope "$CLAUDE_PLUGIN_SCOPE"
claude plugin list
```

更新後はClaude Codeを再起動してください。

marketplaceの取得と、インストール済みパッケージの更新は分けて確認します。同じバージョンとして公開された変更は、更新コマンドだけでは反映されない場合があります。「最新」と表示された場合は公開バージョンを確認し、キャッシュ内のファイルを直接編集しないでください。

コマンドは2026-09-06時点のCLIヘルプと、[Codexのmarketplace管理](https://developers.openai.com/plugins/build/plugins)、[Claude Codeの更新仕様](https://code.claude.com/docs/en/plugins-reference#plugin-update)を確認しています。

## 公開する役割Catalog

役割の目的、責務、禁止事項、権限、受け渡し関係の正式な定義は`roles/catalog.yml`だけである。他pluginへ内部配置を探索させず、検査済みの版固定JSONを公開成果物として書き出す。

roleの`sends`と`receives`は可能なartifact型、`relations`は実際に許可する送信経路である。workerとreviewerが`research_request`を送る場合はresearcherへのrelationを持ち、researcherの`research_report`が依頼元へ戻るrelationも持つ。

### role通信経路の構造検査宣言

- 基準資料: `roles/catalog.yml`のrolesとrelations
- 入力: 構文解析済みRole Catalog
- 正規化: role IDとartifact型を文字列集合として扱い、relationをfrom/toの有向辺として扱う
- 合格述語: 各roleが宣言するすべての`sends`は同じroleをfromとするrelationの`sends`に現れ、各`receives`は同じroleをtoとするrelationの`sends`に現れる
- 診断: 経路のないrole IDとartifact型を示して停止する
- 正例: worker→researcherの`research_request`とresearcher→workerの`research_report`。反例: workerの`sends`だけにある`research_request`。境界例: `permits`が空でもartifact送信経路は成立する
- 意味評価として残す範囲: 調査依頼が必要か、調査結果が十分か、どのinstanceへ送るか

```bash
# <package root> は導入した agent-roles package の root（このrepositoryでは plugins/agent-roles）
python3 "<package root>/scripts/export_catalog.py" \
  --target "$HOME/.config/agent-roles/catalogs/builtin@2.json"
```

Fleetなどの利用側は、この明示的に書き出したJSONを入力として受け取る。利用側が役割名や役割本文を複製してはならない。Catalogの書き出しはagent instanceの作成、タスク割当、Fleet起動を行わない。

役割を選ぶ基準、兼任禁止、成果報告から受容までの業務ルールとBDDは、[エージェント役割割当の業務知識と振る舞い](docs/2026-09-02-エージェント役割割当-業務知識と振る舞い.md)を正式な定義とする。

## 検証

```bash
bash scripts/validate.sh
```
エージェントごとの役割・責務・関係性を定義するプラグイン marketplace

## 実行契約の検証と配布

保守用tool（doctor / lint-consumer-contract / evaluate-skills / release / test-hardening / validate-plugin-repository）の実装元は兄弟checkoutの `../harness-tools/` であり、このrepositoryは複製を持たない。`scripts/validate.sh` は `../harness-tools/tools/` の実在を確認してから呼び、無ければ止まる。CIの `validate.yml` も `harness-tools` を兄弟checkoutして `harness-tools/ci/validate.sh` を実行する。呼び方は `../harness-tools/README.md` にある。

`python3 ../harness-tools/tools/doctor.py --repository <このrepositoryの絶対path> --repo <対象repository>` はCLI構文、公開skillと設定・依存の解決を読み取り専用で診断する。設定解決を含めない検査は `--distribution-only` を明示する。

`bash scripts/validate.sh` は機能・不正入力・配布の検証を行い、GitHub Actionsの `validate (ubuntu-latest)` / `validate (macos-latest)` でも実行する。[意味的評価シナリオ](evals/scenarios.json)は `harness-tools` の評価runner（`scripts/run-evals.sh`）で実モデルと別のjudgeモデルへ渡し、モデルID・設定・入力・応答・判定根拠を記録する。criterionの真偽は意味評価の記録であり、CLIの合否にはしない。CLIの非zero終了はadapter失敗、不正な応答、根拠不整合など記録を完了できない操作失敗を示す。人またはエージェントが記録を読み、構造検証とは別に根拠付きで評価する。未実行を成功として扱わない。

version更新は `python3 ../harness-tools/tools/release.py --repo <このrepositoryの絶対path> --plugin <公開plugin名> --version <semver> --notes <変更内容> --breaking <互換性への影響> --migration <移行方法> --checks <codex/claudeの検証結果JSON>` で計画を確認し、`--apply` で両runtimeのmanifestとmarketplaceを更新する。検証結果には未検証も明示できる。配布・外部publishは別操作であり、このcommandでは行わない。

### 破壊的変更と移行

公開入口は同名SKILLの薄い別入口を廃止して一意にした。古い内部SKILL pathを直接参照している呼出元は公開manifestのskillsへ切り替える。設定の一時fileはshell終了では削除されず、返却された絶対pathを次の工程へ渡し、完了・停止時にrun-configのcleanupでそのrunだけを削除する。以前の一時fileや異なる実行identityを再利用せず、新しいrunを開始する。

## このpackageが持つ判断

`agent-roles` は、役割（manager、advisor、worker、reviewer、researcher）が何を産出し、どの権限を持ち、何をしてはならないかの判断を持つ。base branchへ統合できる役割は受容を決めるmanagerだけであること、managerが作業者へ渡す承認範囲に統合を含めないこと、workerが片付けてよい範囲もここにある。統合してよいかは利用者とrepositoryの方針が決め、mergeしてよい機械状態は `agent-work-policy` が決める。
