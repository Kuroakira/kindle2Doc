# Kindle2Sum

Kindleアプリを自動でページめくりしながらキャプチャし、Gemini Vision APIで画像から直接ページ要約を生成するツールです。RAG（Retrieval-Augmented Generation）用のデータ作成に最適です。

## 機能

- ✅ Kindleアプリの自動ページキャプチャ
- ✅ **自動フォーカス機能（macOS）** - コマンド実行後、自動でKindleアプリにフォーカス
- ✅ **マルチディスプレイ対応** - 特定ウィンドウのみをキャプチャ
- ✅ **縦書き・横書き対応** - 日本語縦書きの本にも対応
- ✅ 最終ページの自動検出
- ✅ **AI要約生成（Gemini Vision API）** - 画像から直接テキストを読み取り要約
- ✅ Markdown形式での出力
- ✅ **Google Docsへのアップロード（オプション）** - 要約結果をGoogle Docsに保存可能

## 必要なもの

### システム要件

- Python 3.9以上
- macOS（PyAutoGUIがmacOSに対応）
- Google Cloud アカウント

### Google Cloud API認証情報

以下のAPIを使用するため、認証情報が必要です：

1. **Google Gemini API（必須）** - AI要約生成（画像から直接）
   - API Key認証が必要
   - 詳しい手順は [GEMINI_SETUP.md](GEMINI_SETUP.md) を参照

2. **Google Docs API（オプション）** - ドキュメントアップロード
   - OAuth認証が必要（要約をDocsにアップロードする場合のみ）
   - 詳しい手順は [GOOGLE_SETUP.md](GOOGLE_SETUP.md) を参照

**料金について**:
- Gemini API: 無料枠（1日あたり1,500リクエスト、月間1500万トークン）、詳細は [GEMINI_SETUP.md](GEMINI_SETUP.md)

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd kindle2md
```

### 2. 仮想環境の作成と有効化

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. Google API認証情報の設定

#### Gemini API（必須・要約生成用）
[GEMINI_SETUP.md](GEMINI_SETUP.md) の手順に従って、API Keyを取得し設定：

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

#### Google Docs API（オプション・アップロード用）
要約をGoogle Docsにアップロードする場合のみ必要です。
[GOOGLE_SETUP.md](GOOGLE_SETUP.md) の手順に従って、OAuth認証情報を取得し配置：

```bash
mkdir -p credentials
mv ~/Downloads/credentials.json credentials/
```

### 5. Kindle推奨設定（精度向上のため）

Kindleアプリで以下の設定を推奨します：

1. **フォントサイズ**: できるだけ大きく設定
2. **ウィンドウサイズ**: フルスクリーンまたは最大化
3. **明るさ**: 明るめに設定
4. **余白**: 可能であれば余白を減らす

これらの設定により、Gemini Vision APIの認識精度が大幅に向上します。

## 使い方

### 事前チェック（推奨）

自動フォーカス機能が正しく動作するか確認するには：

```bash
source venv/bin/activate
python test_focus.py
```

### 基本的な使い方

1. Kindleアプリを開き、要約したい本の最初のページを表示
2. ターミナルで以下のコマンドを実行

```bash
source venv/bin/activate

# 環境変数を設定（まだの場合）
export GEMINI_API_KEY="your-gemini-api-key"

# 横書きの本（デフォルト）
python kindle2sum.py --title "本のタイトル" --save-summary summary.md

# 縦書きの本（日本の本の多く）
python kindle2sum.py --title "本のタイトル" --page-direction left --save-summary summary.md

# 要約をGoogle Docsにもアップロード
python kindle2sum.py --title "本のタイトル" --save-summary summary.md --upload-to-docs
```

3. **自動的にKindleアプリにフォーカスが移ります**（macOSのみ）
4. 2秒後に自動的にキャプチャが開始されます
5. 最終ページまで自動的にキャプチャし、Gemini Vision APIで要約を実行します

**重要**: 日本語の縦書きの本は `--page-direction left` を指定してください（左矢印キーでページ送り）。

### オプション

```bash
# タイトルを指定
python kindle2sum.py --title "マイブック" --save-summary output.md

# ページ送りの待機時間を変更（デフォルト: 1.5秒）
python kindle2sum.py --title "マイブック" --delay 2.0 --save-summary output.md

# キャプチャ画像を保持（デフォルトでは削除されます）
python kindle2sum.py --title "マイブック" --keep-images --save-summary output.md

# 自動フォーカスを無効化（手動でフォーカスする場合）
python kindle2sum.py --title "マイブック" --no-auto-focus --save-summary output.md

# 別のアプリをキャプチャ（例: Kobo）
python kindle2sum.py --title "マイブック" --app-name "Kobo" --save-summary output.md

# 縦書きの本（左矢印でページ送り）
python kindle2sum.py --title "決定力" --page-direction left --save-summary output.md

# 使用するGeminiモデルを変更
python kindle2sum.py --title "マイブック" --gemini-model gemini-1.5-pro --save-summary output.md

# 3ページだけテスト実行
python kindle2sum.py --title "テスト" --max-pages 3 --save-summary test.md
```

### 全オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--title` | ドキュメントのタイトル | `Kindle Book` |
| `--output-dir` | キャプチャ画像の保存先 | `output` |
| `--delay` | ページ送り後の待機時間（秒） | `1.5` |
| `--max-pages` | 最大ページ数 | `1000` |
| `--page-direction` | ページ送りの方向（`left`=縦書き, `right`=横書き） | `right` |
| `--save-summary` | 要約Markdownファイルパス指定 | なし（必須） |
| `--upload-to-docs` | Google Docsにもアップロード | `False` |
| `--keep-images` | キャプチャ画像を保持 | `False` |
| `--no-auto-focus` | 自動フォーカスを無効化 | `False` |
| `--app-name` | キャプチャするアプリ名 | `Kindle` |
| `--gemini-model` | 使用するGeminiモデル | `gemini-1.5-flash` |
| `--similarity-threshold` | 最終ページ検出閾値（0-10） | `2` |
| `--disable-end-detection` | 最終ページ自動検出を無効化 | `False` |

## 出力形式

生成される要約Markdownファイルの形式：

```markdown
# 本のタイトル
**総ページ数**: 100
**生成方法**: Gemini Vision API（画像から直接要約）

---
## ページ 1

### 要約
ページ1の内容を200-300文字で要約したテキスト...

---
## ページ 2

### 要約
ページ2の内容を200-300文字で要約したテキスト...

...
```

## プロジェクト構成

```
kindle2md/
├── kindle2sum.py          # メインスクリプト
├── src/
│   ├── kindle_capture.py  # Kindleキャプチャモジュール
│   ├── summarizer.py      # AI要約生成モジュール（Gemini Vision API使用）
│   └── google_docs_uploader.py  # Google Docsアップロードモジュール
├── credentials/           # Google API認証情報（.gitignore）
│   └── credentials.json   # Google Docs API認証情報（オプション）
├── output/                # 一時ファイル（.gitignore）
├── requirements.txt       # 依存パッケージ
├── GEMINI_SETUP.md       # Google Gemini API設定ガイド
├── GOOGLE_SETUP.md       # Google Docs API設定ガイド（オプション）
└── README.md             # このファイル
```

## トラブルシューティング

### 自動フォーカスが動作しない

**macOSの場合：**
システム環境設定でアクセシビリティの許可が必要な場合があります。

1. システム環境設定 > セキュリティとプライバシー > プライバシー > アクセシビリティ
2. ターミナルまたはiTerm2にチェックを入れる

**回避策：**
`--no-auto-focus` オプションを使用して手動でフォーカスします：

```bash
python kindle2sum.py --title "本のタイトル" --no-auto-focus --save-summary output.md
```

### マルチディスプレイで全画面がキャプチャされる

自動フォーカスが有効な場合、Kindleウィンドウのみがキャプチャされます。
もし全画面がキャプチャされている場合は、Kindleアプリが正しく認識されていない可能性があります。

**解決方法：**
- Kindleアプリが起動しているか確認
- `--app-name` オプションで正確なアプリ名を指定

### Gemini API認証エラー

```
API key not configured
```

環境変数 `GEMINI_API_KEY` が設定されているか確認してください：

```bash
echo $GEMINI_API_KEY
# API Keyが表示されるはず
```

詳しくは [GEMINI_SETUP.md](GEMINI_SETUP.md) を参照。

### Google Docs API認証エラー

`credentials/credentials.json` が正しく配置されているか確認してください。詳しくは [GOOGLE_SETUP.md](GOOGLE_SETUP.md) を参照。

### 要約の精度が低い

- `--delay` オプションでページ送りの待機時間を長くしてみてください（画像のブレを防ぐ）
- Kindleアプリの表示サイズを大きくすると認識精度が向上する場合があります
- フォントサイズを大きくすると、Gemini Vision APIの認識精度が向上します

### 要約の品質を上げたい

- `--gemini-model gemini-1.5-pro` でより高品質なモデルを使用
- ただし、コストが高く、無料枠が少ないので注意

### キャプチャが止まらない

最終ページの検出に失敗している可能性があります。`Ctrl+C` で中断してください。

## 注意事項

- このツールは個人的な使用を想定しています
- 著作権法を遵守して使用してください
- **キャプチャ中はマウスやキーボードを操作しないでください**
- macOS以外のOSでは自動フォーカス機能は使用できません
- API使用量に注意してください（無料枠を超えると課金されます）

## ライセンス

MIT License

## 貢献

バグ報告や機能要望はIssueでお願いします。
