# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

日本語の文を見て英語で答える **日→英専用クイズアプリ**（EIGO NO PARTNER）。
サーバー不要・単一HTMLファイルで動作。ブラウザで `english_test.html` を開くだけで使用可能。

## 重要なファイル

- `english_test.html` — アプリ本体。UI（CSS）、データ読込、クイズロジック、履歴管理が単一ファイルに収まっている
- `json/words-data.js` — `window.WORDS` 配列。xlsx から build.py で生成される単語データ
- `build.py` — Excel(xlsx) → JSデータ変換スクリプト
- `xlsx/EIGO_NO_PARTNERに出てくる文.xlsx` — 出典データ（Lesson / Part / 英語 / 日本語 の4列構成）
- `.devcontainer/devcontainer.json` + `Dockerfile` — Dev Container 環境（Node.js + pnpm）

## コマンド

| 操作 | コマンド |
|------|----------|
| 単語データの再生成 | `uv run python build.py` |
| 依存関係のインストール | `pnpm install` |

- Python 環境は `uv` で管理（`.python-version` = 3.13、`pyproject.toml`、`uv.lock`）
- 依存: `openpyxl>=3.1.5` のみ

## アーキテクチャ

### データフロー

```
xlsx/出典データ → build.py → json/words-data.js → english_test.html (window.WORDS)
```

1. `build.py` が `xlsx/` 内のExcelを読み、別解展開（人称代名詞・可能形動詞など）を行った上で `window.WORDS = [...]` 形式のJSファイルを生成
2. `english_test.html` が `<script src="json/words-data.js">` でデータを読込

### english_test.html の構成（1つのファイル内）

- **CSS（~1-185行）**: `.note-page` ベースのノート風UI。変数定義は `:root`
- **HTML（~187-190行）**: `<div class="note-page" id="app">` にマウント
- **JS ロジック**:
  - 正規化・比較: `normalizeEn()`, `compareWords()` — 縮約形展開・NFKC正規化・冠詞除去・空白正規化後、完全一致比較
  - 状態管理: `state` オブジェクト（`screen`, `selectedLesson`, `queue`, `currentIndex` など）
  - 描画: `render()` → 画面種別に応じて `renderStart()` / `renderQuiz()` / `renderResult()` / `renderHistory()`
  - 履歴: `localStorage` に保存（`ja2en_quiz_history` キー）
  - 進捗: `localStorage` に `ja2en_quiz_attempted` キーで出題済み問題を記録
  - チャート: SVG で直接描画（`renderChart()`）

### 画面遷移

```
start (レッスン/パート選択) → quiz (問題表示・回答) → result (結果表示) → history (履歴一覧)
```

### 別解展開（build.py 側）

- 人称代名詞: `私は` ↔ `ぼくは` / `僕は` / `ぼくが` / `僕が`
- 可能形: `...ことができます` → `...できる` などの縮約形
- 特殊パターン: `...をみます` → `...を見ます` など

## 編集時の注意点

- `english_test.html` は **単一ファイル・フレームワークなし**。React やビルドツールは使われていない
- CSS は `.note-page` 配下にカプセル化。変数(`--bg`, `--red` など)でテーマ色を管理
- `window.WORDS` の構造 (`lesson`, `part`, `en`, `ja`, `ja_answers`) は build.py 側と固定
- 正誤判定は **ローカルJSのみ**（AI採点なし）
- 履歴はブラウザの `localStorage` に保存され、サーバー送信しない