"""
Google Docsアップロードモジュール
"""
import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleDocsUploader:
    """Google Docsへテキストをアップロードするクラス"""

    # Google APIのスコープ
    SCOPES = ['https://www.googleapis.com/auth/documents',
              'https://www.googleapis.com/auth/drive.file']

    def __init__(self, credentials_path: str = "credentials/credentials.json",
                 token_path: str = "token.json"):
        """
        Args:
            credentials_path: Google API認証情報ファイルのパス
            token_path: アクセストークン保存ファイルのパス
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.docs_service = None
        self.drive_service = None

    def authenticate(self):
        """Google APIの認証を実行"""
        # トークンファイルが存在する場合は読み込み
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(
                self.token_path, self.SCOPES
            )

        # 認証情報が無効または存在しない場合
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # トークンをリフレッシュ
                print("Refreshing access token...")
                self.creds.refresh(Request())
            else:
                # 新規認証
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please follow the setup guide in GOOGLE_SETUP.md"
                    )

                print("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # トークンを保存
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
            print("✓ Authentication successful")

        # サービスを初期化
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def create_document(self, title: str) -> str:
        """
        新しいGoogle Documentを作成

        Args:
            title: ドキュメントのタイトル

        Returns:
            作成されたドキュメントのID
        """
        try:
            document = self.docs_service.documents().create(
                body={'title': title}
            ).execute()

            doc_id = document.get('documentId')
            print(f"✓ Document created: {title}")
            return doc_id

        except HttpError as error:
            print(f"⚠ Error creating document: {error}")
            raise

    def insert_text(self, document_id: str, text: str):
        """
        ドキュメントにテキストを挿入

        Args:
            document_id: ドキュメントID
            text: 挿入するテキスト
        """
        try:
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': text
                    }
                }
            ]

            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            print(f"✓ Text inserted into document")

        except HttpError as error:
            print(f"⚠ Error inserting text: {error}")
            raise

    def get_document_url(self, document_id: str) -> str:
        """
        ドキュメントのURLを取得

        Args:
            document_id: ドキュメントID

        Returns:
            ドキュメントのURL
        """
        return f"https://docs.google.com/document/d/{document_id}/edit"

    def upload_markdown(self, markdown_text: str, title: str = "Kindle Book") -> str:
        """
        MarkdownテキストをGoogle Docsにアップロード

        Args:
            markdown_text: Markdownテキスト
            title: ドキュメントのタイトル

        Returns:
            作成されたドキュメントのURL
        """
        print("\n=== Uploading to Google Docs ===")

        # 認証
        if not self.docs_service:
            self.authenticate()

        # ドキュメント作成
        doc_id = self.create_document(title)

        # テキスト挿入
        self.insert_text(doc_id, markdown_text)

        # URL取得
        url = self.get_document_url(doc_id)
        print(f"\n✓ Upload complete!")
        print(f"Document URL: {url}")

        return url


if __name__ == "__main__":
    # テスト実行
    uploader = GoogleDocsUploader()

    try:
        # テスト用のテキスト
        test_text = """# Test Document

This is a test document created by Kindle2MD.

## Features
- Automatic page capture
- OCR processing
- Google Docs upload

Thank you for using Kindle2MD!
"""

        url = uploader.upload_markdown(test_text, "Kindle2MD Test")
        print(f"\nTest document created: {url}")

    except FileNotFoundError as e:
        print(f"\n⚠ {e}")
    except Exception as e:
        print(f"\n⚠ Error: {e}")
