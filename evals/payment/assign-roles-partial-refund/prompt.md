---
plugins: ["../../../plugins/agent-roles"]
description: 仕事の説明と使えるエージェントの数から役割を割り当てさせ、要る役割を兼任で埋めないか、worker に統合させないか、reviewer を受け入れの前に置くか、担い手のいない役割と未検証の範囲を報告するかを確かめる。
tags: [agent-roles]
max_turns: 60
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite, Write, Edit, Bash]
---

作業場所の `job.md` にある仕事を、使えるエージェントで進めたいです。エージェントそれぞれへの役割の割り当てを決めて、`out/roles.md` に書いてください。エージェントの起動や pane の作成はしないでください。GitHub などの外部のサービスにも触れないでください。

最後に、日本語で短く報告してください。
