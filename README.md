# Agent Roles Plugins

複数agentへ役割を割り当てるClaude Code/Codex両対応marketplaceである。旧`agent-roles`のmanager、advisor、worker、reviewer、researcherを移植し、role definitionとrole間の関係をYAML catalogとして検査可能にした。

このpluginはrole assignmentだけを扱う。agent instance、task、model、Herdr pane、runtime binding、UI layoutはFleet pluginの責務である。

## こんなときに使う

**複数のAIエージェントへ、成果物に対する責任と禁止事項を一貫して与えたいときに使う。** 役割名だけでなく、何を担当し、誰へ渡し、何を兼任してはいけないかを検査可能なCatalogとして管理する。

- managerが全体を監視し、workerへ作業を割り当てる責務を揃えたい
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

### Codex

```bash
codex plugin marketplace add nakamori-naoya/agent-roles-plugins
codex plugin add agent-roles@agent-roles
```

### Claude Code

```bash
claude plugin marketplace add nakamori-naoya/agent-roles-plugins
claude plugin install agent-roles@agent-roles
```

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

## 実行契約の検証と配布

`python3 scripts/doctor.py --repository . --repo <対象repository>` はCLI構文、公開skillと設定・依存の解決を読み取り専用で診断する。設定解決を含めない検査は `--distribution-only` を明示する。

`bash scripts/validate.sh` は機能・不正入力・配布の検証を行い、GitHub Actionsの `validate (ubuntu-latest)` / `validate (macos-latest)` でも実行する。[意味的評価シナリオ](evals/scenarios.json)は `scripts/evaluate-skills.py` で実モデルと別のjudgeモデルへ渡し、モデルID・設定・入力・応答・判定根拠を記録する。モデル評価は構造検証と別に実施し、未実行を成功として扱わない。

version更新は `python3 scripts/release.py --plugin <公開plugin名> --version <semver> --notes <変更内容> --breaking <互換性への影響> --migration <移行方法> --checks <codex/claudeの検証結果JSON>` で計画を確認し、`--apply` で両runtimeのmanifestとmarketplaceを更新する。検証結果には未検証も明示できる。配布・外部publishは別操作であり、このcommandでは行わない。

### 破壊的変更と移行

公開入口は同名SKILLの薄い別入口を廃止して一意にした。古い内部SKILL pathを直接参照している呼出元は公開manifestのskillsへ切り替える。設定の一時fileはshell終了では削除されず、返却された絶対pathを次の工程へ渡し、完了・停止時にrun-configのcleanupでそのrunだけを削除する。以前の一時fileや異なる実行identityを再利用せず、新しいrunを開始する。
