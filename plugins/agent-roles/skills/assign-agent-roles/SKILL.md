---
name: assign-agent-roles
description: 複数agentへmanager、advisor、worker、reviewer、researcherの役割を割り当て、成果物・権限・受け渡し・越境禁止を定める。agent fleetの起動やpane操作は行わない。
---

# assign-agent-roles

このskillを読み終えたagentは、検査済みのRole Catalogから仕事に必要な役割だけを選び、各役割の目的・完了条件・停止条件・期待する成果物・許可された受け渡し経路を決め、Fleetなど別の実行機構へ検査済みCatalogを渡せる。役割は作業手順ではなく、産出する成果物の型で分ける。

## 入力

依頼された仕事と、その完了条件・停止条件を受け取る。役割と関係の正式な定義は `../../roles/catalog.yml` である（このSKILL.mdがある入口directoryを基準にした相対path）。

## 判断基準

### 役割は成果物の型で立てる

役割は、その役割が産出する成果物の型が仕事に要るときだけ立てる。全roleを常に立てる必要はない。managerは目的、完了条件、停止条件、最終判断を持つ。advisorは選択肢とトレードオフを返し、合否は判定しない。workerは成果物と検証結果を返し、自分の成果物を評価済みにしない。reviewerは作業経緯から独立した再現可能な反証を返し、修正はしない。researcherは出典と時点のある事実を返し、推奨はしない。reviewerの再現可能な指摘の採否はmanagerが決め、未検証の範囲を「問題なし」へ変えない。

### 兼任で埋めない

必要なroleの担い手がいないとき、別roleへ暗黙に兼任させない。advisorが助言した成果物を同じadvisorがreviewすること、workerが自分の成果物をreviewすることは越境である。

agentが一体だけの仕事には、この役割の割り当てを使わない。そのagentは成果物を作る役だけを担い、受容と統合は利用者が決める。

### 統合できるのはmanagerだけである

共有の統合先（base branch）へ成果物を統合できる役割は、受容を決めるmanagerだけである（Catalogの `integrate`）。受容する者と統合する者が分かれると、受容していない成果物が統合先に入るからである。受容と統合の順序を一者が持つことで、どの成果物をどの順に入れ、残りの作業者にいつ追従させるかも一つに決まる。workerは完了報告で止まり、自分の成果物を統合しない。古いbaseのままの統合を止めるのは、この役割の定義ではなく、統合する操作の側の前提（headがbaseの先端を含むこと）である。

統合できる役割と、統合してよいかは別の問いである。統合してよいかを最後に決めるのは、利用者とrepositoryの方針である。利用者が統合を自分に留めているなら、managerは受容と統合の順序を提案するところで止まる。managerが統合するときは、一件ずつ統合し、統合でbaseが進んだら残りの作業者へ追従を指示する。

managerが作業者へ利用者の承認範囲を渡すときは、統合（merge）を含めない。承認の中継で、統合の権限が作業者へ移ってしまうからである。

### 片付けてよい範囲

workerが片付けてよいのは、自分に割り当てられた作業場所と作業branchだけであり、それもmanagerの指示に従う。その外にある作業場所、branch、実行資源を破棄するかは、managerが決める。

### Catalogへ書くもの

Catalogへはrole definitionとassignmentだけを書く。agent instance、model、task、Herdr pane、runtime binding、UI layoutはFleet側の関心なので書き足さない。

## 手順

### 1. Catalogを検査する

`python3 ../../scripts/validate_catalog.py ../../roles/catalog.yml --output-json` でCatalogを検査する。終了code 0なら、標準出力の検査済みCatalog JSONを使う。終了code 2なら標準エラーに `[error] <理由>` が出るので、そのCatalogは使わず、直してから続ける。

### 2. 必要なroleだけを割り当てる

判断基準に従い、割り当てるroleと割り当てないroleを決め、roleごとの目的、完了条件、停止条件、期待する成果物、許可された受け渡し経路（Catalogの `relations`）を定める。

### 3. 検査済みCatalogを書き出す

Fleetなど別の実行機構へ渡す場合は、相手にplugin内部のfileを探させず、版を含む利用者管理のpathへ検査済みJSONを書き出す。`python3 ../../scripts/export_catalog.py --target "$HOME/.config/agent-roles/catalogs/builtin@2.json"` を実行すると、成功なら標準出力に `{"ok": true, "result": ...}` が出て、targetへ検査済みJSONが書かれる。失敗なら終了code 2と `{"ok": false, "error": ...}` が出る。既存の内容と異なるときもここで止まるので、変更内容を確かめて版の扱いを決めた後だけ `--replace` を付けて再実行する。書き出したものは役割Catalogの固定版であり、Fleetの実行状態ではない。

## 停止条件

止まるのは、toolが失敗したとき、契約外の依頼のとき、越境なしに埋められない不足があるときである。`validate_catalog.py` または `export_catalog.py` が失敗したら、理由を変えずに返す。必要なroleの担い手がいなければ、兼任で埋めず、不足するroleとその成果物を報告する。依頼がagent instanceの作成、task割当、Fleet起動、pane操作を含むなら、それらは `agent-fleet` の関心として返す。止まるときは、検査済みの範囲、止めた判断、不足しているroleまたは入力、再開に必要な情報を返す。

判断の揺れでは止まらない。どのroleを立てるか、reviewerやresearcherを省いてよいかが仕事の完了条件から一意に決まらないときは、成果物の型から最も筋の良い割り当てを仮説として採り、採らなかった割り当てと、省いた場合に未検証になる範囲を出力に明示して、確認は割り当て結果とともに求める。

## 出力

割り当てるroleと割り当てないrole、roleごとの目的・完了条件・停止条件・期待する成果物、許可された受け渡し経路、reviewer不在などで未検証になる範囲を返す。Catalogを書き出したときは、その絶対pathも返す。
