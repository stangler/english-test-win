# 日→英 テスト — EIGO NO PARTNER

日本語の文を見て英語で答える、日→英専用の練習クイズです。
`translation-test-app` からクラウドインフラ（Vercel / Neon / next-auth / Resend / AI採点）を
すべて除去し、`english-word-typing-app` と同様の **単一HTMLファイル構成** に作り直したものです。

- サーバー不要・DB不要・認証不要・インターネット接続不要（フォント読み込みを除く）
- `english_test.html` をブラウザで開くだけで動作
- 英→日モード・AI採点（Gemini/OpenRouter）・ログイン・履歴保存は非搭載

---

## 使い方

1. `english_test.html` をダブルクリックしてブラウザで開く
2. レッスン・パートを選んで「開始」
3. 日本語の問題文を見て英語で入力 → Enter または「判定」
4. テスト後は「履歴を見る」で過去の結果を確認

正誤判定はローカルのJSのみで行われます（縮約形展開・冠詞除去・NFKC正規化した上で完全一致比較）。

---

## 履歴の確認

テスト履歴はブラウザの `localStorage` に保存されます。

- 「📊 履歴を見る」で全履歴を一覧表示
- 「パート別統計」をクリックすると、選択したレッスン/パートの履歴のみに絞り込み
- 「すべて表示」または「✕ クリア」でフィルタを解除
- 上部の「表示回数 / 平均正答率 / 最高記録」はフィルタ後の値を反映

---

## ファイル構成

```
english-test-app/
├── english_test.html     # アプリ本体（UI + ロジック、単一ファイル）
├── json/
│   └── words-data.js     # window.WORDS = [...] 形式の単語データ（build.pyで生成）
├── xlsx/
│   └── EIGO_NO_PARTNERに出てくる文.xlsx  # 出典データ
├── build.py               # xlsx → json/words-data.js 変換スクリプト
├── pyproject.toml         # プロジェクト設定（uv管理用）
└── README.md
```

## 単語データの再生成

xlsx を差し替えた場合は再生成してください。

```bash
uv run python build.py
```

`xlsx/` 内のExcelファイル（Lesson / Part / 英語 / 日本語の列構成）を読み込み、
`json/words-data.js` を上書き生成します。別解展開（人称代名詞・可能形動詞など）も
`translation-test-app` の `build.py` と同じロジックを流用しています。

---

## translation-test-app との違い

| 項目 | translation-test-app | 本アプリ |
| --- | --- | --- |
| クイズモード | 英→日・日→英 | 日→英のみ |
| フレームワーク | Next.js 14 | なし（静的HTML） |
| DB | PostgreSQL + Prisma | なし（localStorage） |
| 認証 | next-auth + Resend | なし |
| 採点 | 日→英はローカル比較、英→日はAI(Gemini/OpenRouter) | ローカル比較のみ |
| デプロイ | Vercel前提 | ローカルで `english_test.html` を開くだけ |
| 履歴保存 | あり(DB) | あり（ブラウザの localStorage） |
