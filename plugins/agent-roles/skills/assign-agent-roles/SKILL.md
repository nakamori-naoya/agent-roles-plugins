---
name: assign-agent-roles
description: 複数agentへmanager、advisor、worker、reviewer、researcherの役割を割り当て、成果物・権限・受け渡し・越境禁止を定める。agent fleetの起動やpane操作は行わない。
---

# assign-agent-roles

このskillを読み終えたagentは、検査済みのRole Catalogから仕事に必要な役割だけを選び、各役割の目的・完了条件・停止条件・期待する成果物・許可された受け渡し経路を決め、Fleetなど別の実行機構へ検査済みCatalogを渡せる。役割は作業手順ではなく、産出する成果物の型で分ける。

## 入力

- 依頼された仕事と、その完了条件・停止条件。
- 役割と関係の正式な定義`../../roles/catalog.yml`。pathはこのSKILL.mdがある入口directoryを基準にした相対pathである。

## 判断基準

### 役割は成果物の型で立てる

`validate_catalog.py` が終了code 0を返したCatalogだけを使う。役割は、その役割が産出する成果物の型が仕事に要るときだけ立てる。全roleを常に立てる必要はない。managerは目的、完了条件、停止条件、最終判断を持つ。advisorは選択肢とトレードオフを返し、合否は判定しない。workerは成果物と検証結果を返し、自分の成果物を評価済みにしない。reviewerは作業経緯から独立した再現可能な反証を返し、修正はしない。researcherは出典と時点のある事実を返し、推奨はしない。reviewerの再現可能な指摘の採否はmanagerが決め、未検証の範囲を「問題なし」へ変えない。

### 兼任で埋めない

必要なroleの担い手がいないとき、別roleへ暗黙に兼任させない。advisorが助言した成果物を同じadvisorがreviewすること、workerが自分の成果物をreviewすることは越境である。

### 統合するのはmanagerだけである

共有の統合先（base branch）へ成果物を統合するのは、受容を決めるmanagerだけである（Catalogの `integrate`）。workerは完了報告で止まり、自分の成果物を統合しない。統合の順序を知らない役割が統合すると、先に入った変更を含まない古いbaseのまま統合され、統合先が壊れるからである。managerは受容した成果物を一件ずつ統合し、統合でbaseが進んだら、残りの作業者へbaseへの追従を指示する。共有の作業場所、branch、実行資源を破棄するかを決めるのもmanagerである。agentが一体だけの仕事では、そのagentがmanagerを兼ねるので、この区別は結果を変えない。

### Catalogへ書くもの

Catalogへはrole definitionとassignmentだけを書く。agent instance、model、task、Herdr pane、runtime binding、UI layoutはFleet側の関心なので書き足さない。

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
| `python3 ../../scripts/export_catalog.py --target "$HOME/.config/agent-roles/catalogs/builtin@1.json"` | 基準資料`../../roles/catalog.yml` | stdoutに`{"ok": true, "result": ...}`、targetへ検査済みJSON | 終了code 2、stdoutに`{"ok": false, "error": ...}`。既存内容が異なる場合はここで止まる | 変更内容を確認して版の扱いを決めた後だけ`--replace`を付けて再実行する |

書き出した成果物は役割Catalogの固定版であり、Fleetの実行状態ではない。

## 停止条件

止まるのは、toolが失敗したか、契約外の依頼か、越境なしに埋められない不足があるときである。

- `validate_catalog.py`または`export_catalog.py`が失敗した。理由を変えずに返す。
- 必要なroleの担い手がいない。兼任で埋めず、不足するroleとその成果物を報告する。
- 依頼がagent instanceの作成、task割当、Fleet起動、pane操作を含む。これらは`agent-fleet`の関心として返す。

止まるときは、検査済みの範囲、止めた判断、不足しているroleまたは入力、再開に必要な情報を返す。

判断の揺れでは止まらない。どのroleを立てるか、reviewerやresearcherを省いてよいかが仕事の完了条件から一意に決まらないときは、成果物の型から最も筋の良い割り当てを仮説として採り、採らなかった割り当てと省いた場合に未検証になる範囲を出力に明示して、確認は割り当て結果とともに求める。

## 出力

- 割り当てるroleと、割り当てないrole。
- roleごとの目的、完了条件、停止条件、期待する成果物。
- 許可された受け渡し経路。
- reviewer不在など未検証になる範囲。
- 必要なら書き出した検査済みCatalog JSONの絶対path。
