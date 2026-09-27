# 期待する判定

この較正の資料は、2026-09-27 の1回目の実行（claude plugin eval、`--runs 1 --ablation none`）で作られた `roles.md` と、実行の担当の最後の報告（`out/trace.jsonl` に写した）である。下の判定は、eval を組んだ担当が割り当て、報告、`job.md` を読んで出したもので、採点役がこれを再現できるかで採点の形を確かめる。

採点役には、このファイルを読ませない。

## 判定

- roles-from-artifacts: PASS
- no-implicit-double-duty: PASS（境目）
- integration-boundary: PASS
- review-before-acceptance: PASS
- unverified-reported: PASS
- research-before-design: PASS
- independent-security-review: PASS

## 理由

割り当ては、manager、researcher、worker、reviewer を立て、立てない advisor の理由も書いている。worker は完了報告で止まり、manager は受け入れの判断と統合の手順の提案で止まり、統合は利用者が行う。受け入れは reviewer の反証の後に置かれている。researcher は出典と確認日時の付いた事実を返し、設計の推奨をしない。他店舗の確かめは、実装した Codex とは別の Claude-B が行う。

no-implicit-double-duty は、Claude-B が researcher と reviewer を段を分けて担う。兼ねることを明示し、同じ成果物の作る側と確かめる側を兼ねてはいないので PASS としたが、一体に二つの役割を持たせることを越境と読むかで分かれうるので境目とした。
