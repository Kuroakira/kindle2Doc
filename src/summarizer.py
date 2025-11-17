"""
要約生成モジュール - Google Gemini APIを使用して画像から直接要約を生成
"""
import google.generativeai as genai
from PIL import Image
from pathlib import Path
from typing import List, Optional, Union
import os


class Summarizer:
    """画像から直接要約を生成するクラス（Gemini Vision）"""

    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        """
        Args:
            model_name: 使用するGeminiモデル名
            api_key: Gemini API Key（Noneの場合は環境変数から取得）
        """
        self.model_name = model_name

        # API Keyの設定
        if api_key is None:
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY environment variable not set. "
                    "Please set it or pass api_key parameter."
                )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def summarize_page_from_image(self, image_path: Path, page_number: int) -> str:
        """
        画像から直接テキストを読み取り要約

        Args:
            image_path: ページ画像のパス
            page_number: ページ番号

        Returns:
            要約テキスト
        """
        try:
            # 画像を読み込み
            image = Image.open(image_path)

            prompt = f"""この画像は本のページ{page_number}です。画像内のテキストを読み取り、内容を箇条書きで要約してください。

要約の要件：
- 3-5個の箇条書き形式（各項目は独立した意味単位）
- ページ内で完結している内容のみを抽出
- 文章が途中で切れている部分は除外する
- 重要なポイントのみを抽出
- 各項目は簡潔に（1項目あたり50-100文字程度）
- 日本語で要約
- RAG（検索）用途に最適化された形式

出力形式：
- 項目1の内容
- 項目2の内容
- 項目3の内容

重要：
- 箇条書きの内容のみを出力してください
- 「このページのテキストを要約します」「以下のように要約できます」などの前置き文は不要です
- 箇条書き（- で始まる行）だけを出力してください"""

            response = self.model.generate_content([prompt, image])
            return response.text.strip()

        except Exception as e:
            print(f"⚠ Error summarizing page {page_number}: {e}")
            return f"（ページ{page_number}の要約生成に失敗しました: {e}）"

    def summarize_pages_from_images(
        self,
        image_paths: List[Path],
        show_progress: bool = True
    ) -> List[str]:
        """
        複数の画像から要約を生成

        Args:
            image_paths: 各ページの画像パスリスト
            show_progress: 進捗表示するかどうか

        Returns:
            各ページの要約リスト
        """
        summaries = []
        total = len(image_paths)

        for i, image_path in enumerate(image_paths, 1):
            if show_progress:
                print(f"Summarizing page {i}/{total} from image...")

            summary = self.summarize_page_from_image(image_path, i)
            summaries.append(summary)

        return summaries

    def create_summary_markdown(
        self,
        summaries: List[str],
        title: str = "Book Summary",
        include_image_paths: bool = False,
        image_paths: Optional[List[Path]] = None
    ) -> str:
        """
        要約をMarkdown形式に変換

        Args:
            summaries: 要約リスト
            title: ドキュメントのタイトル
            include_image_paths: 画像パスへのリンクを含めるか
            image_paths: 画像パスリスト（include_image_paths=Trueの場合）

        Returns:
            Markdown形式のテキスト
        """
        markdown_lines = []

        # タイトル
        markdown_lines.append(f"# {title}\n")
        markdown_lines.append(f"**総ページ数**: {len(summaries)}\n")
        markdown_lines.append("**生成方法**: Gemini Vision API（画像から直接要約）\n")
        markdown_lines.append("**要約形式**: 箇条書き（RAG最適化）\n")

        # 各ページの要約
        for i, summary in enumerate(summaries, 1):
            markdown_lines.append(f"\n---\n<!-- Page: {i} -->\n")
            markdown_lines.append(f"{summary}\n")

            # 画像パスへのリンク（オプション）
            if include_image_paths and image_paths and i <= len(image_paths):
                markdown_lines.append(f"\n<!-- Image: {image_paths[i-1]} -->\n")

        return "\n".join(markdown_lines)

    def save_summary_markdown(self, markdown_text: str, output_path: Path):
        """
        要約Markdownをファイルに保存

        Args:
            markdown_text: Markdownテキスト
            output_path: 出力ファイルのパス
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)

        print(f"✓ Summary saved to: {output_path}")

    def process_and_save(
        self,
        image_paths: List[Path],
        output_path: Path,
        title: str = "Book Summary",
        keep_image_links: bool = False
    ) -> str:
        """
        画像から要約生成→Markdown変換→保存を一括実行

        Args:
            image_paths: 各ページの画像パスリスト
            output_path: 出力ファイルのパス
            title: ドキュメントのタイトル
            keep_image_links: 画像パスへのリンクを含めるか

        Returns:
            Markdown形式のテキスト
        """
        print("\n=== Summarization Started (Gemini Vision) ===")

        # 画像から要約生成
        summaries = self.summarize_pages_from_images(image_paths)

        # Markdown変換
        print("\nConverting to Markdown...")
        markdown_text = self.create_summary_markdown(
            summaries,
            title=title,
            include_image_paths=keep_image_links,
            image_paths=image_paths if keep_image_links else None
        )

        # 保存
        self.save_summary_markdown(markdown_text, output_path)

        print(f"\n=== Summarization Complete ===")
        print(f"Total pages processed: {len(image_paths)}")
        print(f"Total summaries: {len(summaries)}")

        return markdown_text


if __name__ == "__main__":
    # テスト実行
    from pathlib import Path

    # テスト用の画像があれば実行
    test_dir = Path("output")
    test_images = sorted(test_dir.glob("page_*.png"))

    if test_images:
        print(f"Found {len(test_images)} test images")
        summarizer = Summarizer()

        output_file = Path("test_summary.md")
        summarizer.process_and_save(
            test_images[:3],  # 最初の3ページだけテスト
            output_file,
            title="Test Book"
        )
    else:
        print("No test images found in output/ directory")
