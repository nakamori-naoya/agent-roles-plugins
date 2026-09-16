---
name: assign-agent-roles
description: 複数agentへmanager、advisor、worker、reviewer、researcherの役割を割り当て、成果物・権限・受け渡し・越境禁止を定める。agent fleetの起動やpane操作は行わない。
---

# assign-agent-roles

このskillを読み終えたagentは、検査済みのRole Catalogから仕事に必要な役割だけを選び、各役割の目的・完了条件・停止条件・期待する成果物・許可された受け渡し経路を決め、Fleetなど別の実行機構へ検査済みCatalogを渡せる。役割は作業手順ではなく、産出する成果物の型で分ける。

## 入力

- 依頼された仕事と、その完了条件・停止条件。
- 役割と関係の正本`../../roles/catalog.yml`。pathはこのSKILL.mdがある入口directoryを基準にした相対pathである。

## 判断基準

| 観察対象 | 判定 |
|---|---|
| Catalogを使えるか | `validate_catalog.py`が終了code 0を返したCatalogだけを使う |
| 役割を立てるか | その役割が産出する成果物の型が仕事に要るときだけ立てる。全roleを常に立てる必要はない |
| 兼任 | 必要なroleの担い手がいないとき、別roleへ暗黙に兼任させない。advisorが助言した成果物を同じadvisorがreviewすること、workerが自分の成果物をreviewすることは越境である |
| managerの権限 | 目的、完了条件、停止条件、最終判断を持つ |
| advisorの成果物 | 選択肢とトレードオフ。合否は判定しない |
| workerの成果物 | 成果物と検証結果。自分の成果物を評価済みにしない |
| reviewerの成果物 | 作業経緯から独立して再現可能な反証。修正はしない |
| researcherの成果物 | 出典と時点のある事実。推奨はしない |
| reviewerの再現可能な指摘 | managerが採否を決める。未検証範囲を「問題なし」へ変換しない |
| Catalogへ書くもの | role definitionとassignmentだけ。agent instance、model、task、Herdr pane、runtime binding、UI layoutはFleet側の関心なので書き足さない |

## 手順

### 1. Catalogを検査する

| 呼び出し | 入力 | 出力 | 失敗の観測 | 失敗時 |
|---|---|---|---|---|
| `python3 ../../scripts/validate_catalog.py ../../roles/catalog.yml --output-json` | Role Catalog YAML | stdoutに検査済みCatalog JSON | 終了code 2、stderrに`[error] <理由>` | 検査が失敗したCatalogは使わず、Catalogを直してから続ける |

### 2. 必要なroleだけを割り当てる

判断基準に従い、割り当てるroleと割り当てないroleを決め、roleごとの目的、完了条件、停止条件、期待する成果物、許可された受け渡し経路（Catalogの`relations`）を定める。

### 3. 検査済みCatalogを公開する

Fleetなど別の実行機構へ渡す場合は、相手にplugin内部fileを探索させず、版を含む利用者管理pathへ検査済みJSONを書き出す。

| 呼び出し | 入力 | 出力 | 失敗の観測 | 失敗時 |
|---|---|---|---|---|
| `python3 ../../scripts/export_catalog.py --target "$HOME/.config/agent-roles/catalogs/builtin@1.json"` | 正本`../../roles/catalog.yml` | stdoutに`{"ok": true, "result": ...}`、targetへ検査済みJSON | 終了code 2、stdoutに`{"ok": false, "error": ...}`。既存内容が異なる場合はここで止まる | 変更内容を確認して版の扱いを決めた後だけ`--replace`を付けて再実行する |

書き出した成果物は役割Catalogの固定版であり、Fleetの実行状態ではない。

## 停止条件

- Catalogの検査が失敗した。
- 必要なroleの担い手がいない（兼任で埋めず、不足を報告する）。
- 依頼がagent instanceの作成、task割当、Fleet起動、pane操作を含む（これらは`agent-fleet`の関心として返す）。

## 出力

- 割り当てるroleと、割り当てないrole。
- roleごとの目的、完了条件、停止条件、期待する成果物。
- 許可された受け渡し経路。
- reviewer不在など未検証になる範囲。
- 必要なら書き出した検査済みCatalog JSONの絶対path。
