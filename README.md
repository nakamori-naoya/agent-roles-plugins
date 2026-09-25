# Agent Roles Plugins

複数のエージェントへ役割（manager、advisor、worker、reviewer、researcher）を割り当てるときの判断を配る、Claude Code/Codex両対応のmarketplaceである。公開するのはpackage `agent-roles` 1件と、skill `assign-agent-roles` 1つである。

## 何を決めるか

[SKILL.md](plugins/agent-roles/skills/assign-agent-roles/SKILL.md)は三つの判断を持つ。役割はその成果物が仕事に要るときだけ立て、兼任で埋めない。baseへ統合できるのは受け入れを決めるmanagerだけで、workerは完了報告で止まる。reviewerの反証は受け入れの前に置く。

役割と関係は `plugins/agent-roles/roles/catalog.yml` に機械が読む形で置き、agent fleetのような実行の仕組みへ渡すときだけ、検査済みのJSONを `~/.config/agent-roles/catalogs/builtin@2.json` へ書き出す。このpluginはエージェントを起動せず、task、model、paneの配置も決めない。

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
