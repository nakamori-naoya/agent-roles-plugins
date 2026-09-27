# Agent Roles Plugins

複数のエージェントへ役割（manager、advisor、worker、reviewer、researcher）を割り当てるときの判断を配る、Claude Code/Codex両対応のmarketplaceである。公開するのはpackage `agent-roles` 1件と、skill `assign-agent-roles` 1つである。

## 何を決めるか

[SKILL.md](plugins/agent-roles/skills/assign-agent-roles/SKILL.md)は三つの判断を持つ。役割はその成果物が仕事に要るときだけ立て、兼任で埋めない。baseへ統合できるのは受け入れを決めるmanagerだけで、workerは完了報告で止まる。reviewerの反証は受け入れの前に置く。

役割ごとの成果物、権限、受け渡し、してはいけないことは `plugins/agent-roles/roles/catalog.yml` だけが持つ。agent fleetのような実行の仕組みへ渡すときだけ、検査済みのJSONを `~/.config/agent-roles/catalogs/builtin@2.json` へ書き出す。このpluginはエージェントを起動せず、task、model、paneの配置も決めない。

## インストール

インストールするのは`agent-roles@agent-roles`です。外部プラグインの追加は不要です。

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

## 検証

```bash
bash scripts/validate.sh
```

`scripts/validate.sh` は、配置とmanifestの一致、SKILLのname、Catalogの構造（各roleの `sends` と `receives` に、`relations` の送信経路があること）を検査する。保守toolの実装元は兄弟checkoutの `../harness-tools/` で、このrepositoryは複製を持たない。

## 判断の eval

skill が外しやすい判断（要る役割を兼任で埋めないこと、worker に統合させないこと、review を受け入れの前に置くこと、担い手のいない役割と未検証の範囲を報告すること）を、`evals/` のケースで確かめる。ケースは手元に置いた仕事の説明だけで組み、エージェントの起動や外部のサービスには触れない。実行は `claude plugin eval` が受け持ち、割り当ての出来は、作業したエージェントとは別の Claude（採点役）が条件ごとに判定し、3 回の多数決と重み付きの 100 点満点で点数にする。`graders/` には、読まずに判定できること（割り当てができたか、skill を使ったか）だけを置く。

共通の条件は `evals/criteria/role-assignment.md`、ケースに固有の条件は `evals/<お題>/<ケース>/grading/criteria.md`、採点役を確かめる資料と期待する判定は `grading/calibration/` にある。条件か採点役への指示を変えたら、先に較正の資料で採点役が期待する判定を再現するかを確かめる。

```bash
claude plugin eval . --case assign-roles-partial-refund --runs 1 --ablation none --keep-temp \
  --scaffold --allow-tools Write Edit Bash --max-cost-usd 5 --no-publish
bash /Users/naoya-nakamoriq/Documents/Github/harness-pluginsv2/harness-tools/tools/grade-eval.sh \
  "$(pwd)/evals/payment/assign-roles-partial-refund" /private/tmp/e-XXXXXX
```

実行と採点の結果は `evals/results/` に書かれ、git の管理から外してある。
