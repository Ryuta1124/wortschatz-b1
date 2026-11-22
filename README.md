# Wortschatz B1

ドイツ語の単語を毎日少しずつ覚えるための、4択クイズ形式の学習アプリです。
HTMLファイル1つで動き、サーバーもインストールも要りません。

Goethe-Zertifikat B1 のワードリストを出発点に、DTZ（Deutsch-Test für Zuwanderer）の単語を加え、
A1・A2 のワードリストでレベルを付けた約2,900語で使っています。
**ただし、このリポジトリには単語データ本体は含まれていません**（理由は「データについて」を参照）。
動作を試せるように、自作の例文付きサンプル24語が入っています。

## できること

- **4択クイズ**：ドイツ語を見て意味を選ぶ／英語・日本語を見てドイツ語を選ぶ（向きを切り替え可能）
- **訳の言語**：英語または日本語
- **間隔反復**：正解した単語は 1 → 2 → 4 → 8 → 16 → 32 日後に再出題。間違えた単語は同じセット内でもう一度出題
- **1日の目標**（10/20/30/50問）と連続学習日数
- **発音**：ブラウザの音声合成でドイツ語を読み上げ（自動再生のオン／オフ）
- **例文**：回答後にドイツ語の例文と英訳を表示し、例文も読み上げ可能
- **レベル・品詞で絞り込み**：A1 / A2 / B1 を自由に組み合わせ、名詞・動詞・その他
- **冠詞の色分け**：der（青）・die（赤）・das（緑）
- **画面表示はドイツ語**：説明文もドイツ語にして、小さなところからドイツ語に慣れる
- 学習記録はブラウザ（localStorage）に保存。端末ごとに別管理

## 使い方

```bash
python scripts/build.py
```

`dist/wortschatz.html` ができるので、ブラウザで開きます。
`data/words.json` があればそれを、なければ `data/sample-words.json` を使います。

キーボード操作：`1`–`4` で回答、`Enter` で次へ、`S` で単語の発音、`B` で例文の発音。

## データについて

アプリ本体（`app/template.html`）とスクリプトはこのリポジトリで公開していますが、
単語リスト・例文のデータは公開していません。

- 元になったワードリスト（Goethe-Institut / ÖSD などが発行する PDF）には、
  発行元の許可なくネットワーク上で公開・保存することを禁じる表示があります。
- 実際に使っているデータには、ワードリストの例文がそのまま多数含まれています。

自分用のデータを作る場合は、ワードリストの PDF を各自で入手し、
`scripts/` のスクリプトで見出し語と例文を取り出してください（下記）。
訳や例文の英訳は自動では作られないため、別途用意する必要があります。

### データ形式

`data/words.json` は次の7項目の配列のリストです。

```json
["der Apfel", "apple", "りんご", "n", "Ich esse jeden Morgen einen Apfel.", "I eat an apple every morning.", "A1"]
```

| 位置 | 内容 |
|---|---|
| 0 | ドイツ語（名詞は冠詞付き） |
| 1 | 英語の意味 |
| 2 | 日本語の意味 |
| 3 | 品詞：`n` 名詞 / `v` 動詞 / `o` その他 |
| 4 | 例文（ドイツ語） |
| 5 | 例文の英訳 |
| 6 | レベル：`A1` / `A2` / `B1` |

学習記録は行の位置（番号）で管理しているので、単語を追加するときは末尾に足してください。

## スクリプト

`pdftotext`（poppler または xpdf）と Python 3 が必要です。

| スクリプト | 役割 |
|---|---|
| `scripts/extract_wordlist.py` | 2段組のワードリスト PDF から見出し語と最初の例文を取り出す |
| `scripts/assign_levels.py` | A1・A2 のワードリストと照合して各単語にレベルを付ける |
| `scripts/build.py` | データをテンプレートに埋め込んで `dist/wortschatz.html` を作る |

```bash
python scripts/extract_wordlist.py B1_Wortliste.pdf 16 102 b1_entries.json
pdftotext -enc UTF-8 -layout A1_Wortliste.pdf a1.txt
pdftotext -enc UTF-8 -layout A2_Wortliste.pdf a2.txt
python scripts/assign_levels.py data/words.json a1.txt a2.txt
python scripts/build.py
```

自動抽出は完全ではありません（2段組の崩れで例文が混ざる・途切れるなど）。
B1 リストでは約1割の例文を手作業で直しました。

## 作成記録

どのように作ったかは [docs/development-log.md](docs/development-log.md) にまとめています。
アプリと訳・例文の英訳の作成には、AI アシスタント（Claude）を使いました。

## ライセンス

プログラム（`app/`・`scripts/`）は MIT ライセンスです。[LICENSE](LICENSE) を参照してください。
`data/sample-words.json` の例文は自作です。
