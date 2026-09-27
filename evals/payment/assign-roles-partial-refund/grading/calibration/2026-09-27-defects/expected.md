# 期待する判定

この較正の資料は、2026-09-27 の1回目の実行で作られた `roles.md` をもとに、既知の欠陥を埋めて書き直した写しである。埋めた欠陥は三つある。一つ目は、セキュリティの確かめを実装した worker 自身に持たせ、reviewer には書き方だけを見させたこと。二つ目は、利用者が統合を自分に留めているのに、manager が main へ統合するとしたこと。三つ目は、受け入れと統合の後に review を置いたこと。researcher の置き方と、立てた理由、未検証の範囲は元の資料のまま残してある。

採点役には、このファイルを読ませない。

## 判定

- roles-from-artifacts: FAIL
- no-implicit-double-duty: FAIL
- integration-boundary: FAIL
- review-before-acceptance: FAIL
- unverified-reported: PASS
- research-before-design: PASS
- independent-security-review: FAIL

## 理由

no-implicit-double-duty は、worker が自分の成果物のセキュリティを確かめるので、同じ成果物について作る側と確かめる側を兼ねており FAIL とした。integration-boundary は、manager が利用者の許可なく main へ統合するので FAIL とした。review-before-acceptance は、受け入れて統合した後に review を頼む順なので FAIL とした。independent-security-review は、他店舗の確かめを実装した worker が持つので FAIL とした。roles-from-artifacts は、reviewer に書き方と保守性だけを見させており、その成果物を求める完了条件が `job.md` に無いので FAIL とした。セキュリティの確かめを worker へ移したことで、reviewer が仕事に要らない役割になっている。unverified-reported は、advisor を立てないことで残る範囲を書いているので PASS とした。research-before-design は、事実を確かめる役を設計の前に置き、推奨をさせていないので PASS とした。
