# Kindle2MD

Kindleアプリを自動でページめくりしながらキャプチャし、OCRでMarkdownに変換してGoogle Docsにアップロードするツールです。

## 機能

- ✅ Kindleアプリの自動ページキャプチャ
- ✅ **自動フォーカス機能（macOS）** - コマンド実行後、自動でKindleアプリにフォーカス
- ✅ **マルチディスプレイ対応** - 特定ウィンドウのみをキャプチャ
- ✅ **縦書き・横書き対応** - 日本語縦書きの本にも対応
- ✅ 最終ページの自動検出
- ✅ **高精度OCR処理**（日本語・英語対応、tessdata_best使用）
- ✅ Markdown形式への変換
- ✅ Google Docsへの自動アップロード

## 必要なもの

### システム要件

- Python 3.9以上
- macOS（PyAutoGUIがmacOSに対応）
- Tesseract OCR

### Tesseractのインストール

```bash
# Homebrewでインストール
brew install tesseract

# 日本語言語データのインストール
brew install tesseract-lang
```

### Tesseract高精度版のインストール（推奨）

OCRの精度を大幅に向上させるため、高精度版の言語データを使用することを強く推奨します：

```bash
# 言語データディレクトリに移動
cd /opt/homebrew/share/tessdata  # M1/M2 Mac
# または
cd /usr/local/share/tessdata     # Intel Mac

# 既存のjpn.traineddataをバックアップ
mv jpn.traineddata jpn.traineddata.bak

# 高精度版をダウンロード
curl -LO https://github.com/tesseract-ocr/tessdata_best/raw/main/jpn.traineddata
```

**注意**: 高精度版は処理が遅くなりますが、認識精度が大幅に向上します。

### Google Docs API認証情報

Google Cloud ConsoleでOAuth認証情報を取得する必要があります。
詳しい手順は [GOOGLE_SETUP.md](GOOGLE_SETUP.md) を参照してください。

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

### 4. Google API認証情報の配置

[GOOGLE_SETUP.md](GOOGLE_SETUP.md) の手順に従って、`credentials.json` を取得し、`credentials/` ディレクトリに配置してください。

```bash
mv ~/Downloads/credentials.json credentials/
```

### 5. Kindle推奨設定（OCR精度向上のため）

Kindleアプリで以下の設定を推奨します：

1. **フォントサイズ**: できるだけ大きく設定
2. **ウィンドウサイズ**: フルスクリーンまたは最大化
3. **明るさ**: 明るめに設定
4. **余白**: 可能であれば余白を減らす

これらの設定により、OCRの認識精度が大幅に向上します。

## 使い方

### 事前チェック（推奨）

自動フォーカス機能が正しく動作するか確認するには：

```bash
source venv/bin/activate
python test_focus.py
```

このテストスクリプトで以下を確認できます：
- Kindleアプリへの自動フォーカス
- ウィンドウ領域の検出（マルチディスプレイ対応）

### 基本的な使い方

1. Kindleアプリを開き、変換したい本の最初のページを表示
2. ターミナルで以下のコマンドを実行

```bash
source venv/bin/activate

# 横書きの本（デフォルト）
python kindle2md.py --title "本のタイトル"

# 縦書きの本（日本の本の多く）
python kindle2md.py --title "本のタイトル" --page-direction left
```

3. **自動的にKindleアプリにフォーカスが移ります**（macOSのみ）
4. 2秒後に自動的にキャプチャが開始されます
5. 最終ページまで自動的にキャプチャし、Google Docsにアップロードされます

**重要**: 日本語の縦書きの本は `--page-direction left` を指定してください（左矢印キーでページ送り）。

### マルチディスプレイ環境での使用

**自動対応しています！** マルチディスプレイ環境でも、Kindleアプリのウィンドウのみをキャプチャするため、問題なく動作します。

- Kindleアプリがどのディスプレイにあっても自動検出
- 他のディスプレイの内容は含まれません
- フルスクリーンモードでも使用可能

### オプション

```bash
# タイトルを指定
python kindle2md.py --title "マイブック"

# ページ送りの待機時間を変更（デフォルト: 1.5秒）
python kindle2md.py --title "マイブック" --delay 2.0

# 英語の本をキャプチャ
python kindle2md.py --title "My Book" --lang eng

# Markdownファイルとして保存（Google Docsにアップロードしない）
python kindle2md.py --title "マイブック" --save-markdown output.md

# キャプチャ画像を保持（デフォルトでは削除されます）
python kindle2md.py --title "マイブック" --keep-images

# ページ区切りなしでMarkdownを生成
python kindle2md.py --title "マイブック" --no-page-separators

# 自動フォーカスを無効化（手動でフォーカスする場合）
python kindle2md.py --title "マイブック" --no-auto-focus

# 別のアプリをキャプチャ（例: Kobo）
python kindle2md.py --title "マイブック" --app-name "Kobo"

# 縦書きの本（左矢印でページ送り）
python kindle2md.py --title "決定力" --page-direction left
```

### 全オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--title` | ドキュメントのタイトル | `Kindle Book` |
| `--output-dir` | キャプチャ画像の保存先 | `output` |
| `--delay` | ページ送り後の待機時間（秒） | `1.5` |
| `--max-pages` | 最大ページ数 | `1000` |
| `--lang` | OCR言語（`jpn` or `eng`） | `jpn` |
| `--page-direction` | ページ送りの方向（`left`=縦書き, `right`=横書き） | `right` |
| `--no-page-separators` | ページ区切りを追加しない | `False` |
| `--keep-images` | キャプチャ画像を保持 | `False` |
| `--save-markdown` | Markdownファイルパス指定 | なし |
| `--no-auto-focus` | 自動フォーカスを無効化 | `False` |
| `--app-name` | キャプチャするアプリ名 | `Kindle` |

## プロジェクト構成

```
kindle2md/
├── kindle2md.py           # メインスクリプト
├── src/
│   ├── kindle_capture.py  # Kindleキャプチャモジュール
│   ├── ocr_processor.py   # OCR処理モジュール
│   └── google_docs_uploader.py  # Google Docsアップロードモジュール
├── credentials/           # Google API認証情報（.gitignore）
├── output/                # 一時ファイル（.gitignore）
├── requirements.txt       # 依存パッケージ
├── GOOGLE_SETUP.md       # Google API設定ガイド
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
python kindle2md.py --title "本のタイトル" --no-auto-focus
```

### マルチディスプレイで全画面がキャプチャされる

自動フォーカスが有効な場合、Kindleウィンドウのみがキャプチャされます。
もし全画面がキャプチャされている場合は、Kindleアプリが正しく認識されていない可能性があります。

**解決方法：**
- Kindleアプリが起動しているか確認
- `--app-name` オプションで正確なアプリ名を指定

### Tesseractが見つからない

```
pytesseract.pytesseract.TesseractNotFoundError
```

Tesseractがインストールされているか確認してください：

```bash
tesseract --version
```

### Google API認証エラー

`credentials/credentials.json` が正しく配置されているか確認してください。詳しくは [GOOGLE_SETUP.md](GOOGLE_SETUP.md) を参照。

### OCRの精度が低い

- `--delay` オプションでページ送りの待機時間を長くしてみてください
- Kindleアプリの表示サイズを大きくすると精度が向上する場合があります

### キャプチャが止まらない

最終ページの検出に失敗している可能性があります。`Ctrl+C` で中断してください。

## 注意事項

- このツールは個人的な使用を想定しています
- 著作権法を遵守して使用してください
- **キャプチャ中はマウスやキーボードを操作しないでください**（自動フォーカス機能が有効な場合も同様）
- macOS以外のOSでは自動フォーカス機能は使用できません

## ライセンス

MIT License

## 貢献

バグ報告や機能要望はIssueでお願いします。
