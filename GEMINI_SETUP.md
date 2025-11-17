# Google Gemini API Setup Guide

このガイドでは、kindle2sumでGoogle Gemini APIを使用するための設定手順を説明します。

## 前提条件

- Googleアカウント
- Google Cloud Platformのプロジェクト（Vision APIと同じプロジェクトで可）

## セットアップ手順

### 1. Gemini APIの有効化

1. [Google AI Studio](https://aistudio.google.com/) にアクセス
2. Googleアカウントでログイン
3. **または** [Google Cloud Console](https://console.cloud.google.com/) で「Generative Language API」を検索して有効化

### 2. API Keyの取得

#### 方法A: Google AI Studio（推奨・簡単）

1. [Google AI Studio](https://aistudio.google.com/) にアクセス
2. 左側のメニューから「Get API key」をクリック
3. 「Create API key」をクリック
4. 既存のGCPプロジェクトを選択（Vision APIと同じプロジェクトで可）
5. API Keyが表示されるのでコピー

#### 方法B: Google Cloud Console

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 「APIとサービス」→「認証情報」を選択
3. 「認証情報を作成」→「APIキー」を選択
4. APIキーが生成されるのでコピー
5. （推奨）「キーを制限」をクリックし、「Generative Language API」のみに制限

### 3. API Keyの設定

#### 方法1: 環境変数に設定（推奨）

```bash
# 一時的に設定
export GEMINI_API_KEY="your-api-key-here"

# 永続的に設定（推奨）
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### 方法2: .envファイルに設定

```bash
# プロジェクトルートに.envファイルを作成
echo 'GEMINI_API_KEY=your-api-key-here' > .env
```

**注意**: `.env`ファイルは`.gitignore`に含まれているため、Gitにコミットされません。

### 4. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 5. テスト

セットアップが正しく完了したか確認：

```bash
python -c "import google.generativeai as genai; import os; genai.configure(api_key=os.environ.get('GEMINI_API_KEY')); print('✓ Gemini API configured successfully')"
```

エラーが出ない場合、セットアップは成功です。

## 料金について

Google Gemini APIには無料枠があります：

### Gemini 1.5 Flash（推奨・高速）
- **無料枠**: 1日あたり1,500リクエスト、月間1500万トークン
- **有料**: 100万トークンあたり$0.075（入力）、$0.30（出力）

### Gemini 1.5 Pro（高品質）
- **無料枠**: 1日あたり50リクエスト、月間200万トークン
- **有料**: 100万トークンあたり$1.25（入力）、$5.00（出力）

詳細は[公式料金ページ](https://ai.google.dev/pricing)を参照してください。

**推奨モデル**: Gemini 2.5 Flash（バランスの取れた機能、価格とパフォーマンスの最適化）

## モデル選択

kindle2sumでは以下のモデルを選択できます：

- `gemini-2.5-flash` - バランス型・推奨（デフォルト）
- `gemini-2.5-pro` - 高品質・複雑な推論タスク向け
- `gemini-2.5-flash-lite` - 高速・低コスト・高スループット

## トラブルシューティング

### "API key not configured"

環境変数が設定されていません。上記の手順3を確認してください。

```bash
# 環境変数を確認
echo $GEMINI_API_KEY
```

### "API has not been enabled"

Generative Language APIが有効化されていません。手順1を確認してください。

### "Quota exceeded"

無料枠の制限に達しました。翌日まで待つか、課金を有効にしてください。

## セキュリティ注意事項

- API Keyは **絶対にGitにコミットしないでください**
- `.env` は `.gitignore` に含まれていることを確認してください
- API Keyは安全に保管してください
- 本番環境では、API Keyの制限（IP制限、APIスコープ制限）を設定してください
