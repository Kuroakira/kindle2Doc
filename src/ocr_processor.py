"""
OCR処理とMarkdown変換モジュール
"""
import pytesseract
from PIL import Image
from pathlib import Path
from typing import List, Dict, Optional
import json


class OCRProcessor:
    """画像からテキストを抽出してMarkdownに変換するクラス"""

    def __init__(self, lang: str = 'jpn'):
        """
        Args:
            lang: OCRで使用する言語（'jpn'=日本語, 'eng'=英語）
        """
        self.lang = lang
        self.cached_ocr_results: Optional[Dict[str, str]] = None

    def clean_japanese_spaces(self, text: str) -> str:
        """
        日本語テキストから不要なスペースと改行を除去
        - 全てのスペースを削除
        - 改行2回連続（段落区切り）は保持
        - 句読点後の改行は保持
        - それ以外の単独改行は削除

        Args:
            text: クリーニング対象のテキスト

        Returns:
            クリーニング後のテキスト
        """
        if not text:
            return text

        # 1. スペースを除去
        text = text.replace(' ', '')

        # 2. 改行の処理
        # 連続する改行（段落区切り）を一時的に保護
        text = text.replace('\n\n', '<<PARAGRAPH>>')

        # 句読点後の改行を保護
        # 日本語の句読点リスト
        punctuation_marks = ['。', '、', '！', '？', '」', '』', '）', ')', '…', '．', '，']
        for punct in punctuation_marks:
            text = text.replace(f'{punct}\n', f'{punct}<<SENTENCE>>')

        # 残りの単独改行を削除
        text = text.replace('\n', '')

        # 保護したマーカーを元に戻す
        text = text.replace('<<PARAGRAPH>>', '\n\n')
        text = text.replace('<<SENTENCE>>', '\n')

        return text

    def load_cached_ocr_results(self, ocr_results_file: Path) -> bool:
        """
        キャプチャ時に保存されたOCR結果を読み込む

        Args:
            ocr_results_file: OCR結果のJSONファイルパス

        Returns:
            読み込みに成功した場合True
        """
        try:
            if ocr_results_file.exists():
                with open(ocr_results_file, 'r', encoding='utf-8') as f:
                    self.cached_ocr_results = json.load(f)
                print(f"✓ Loaded cached OCR results ({len(self.cached_ocr_results)} pages)")
                return True
        except Exception as e:
            print(f"⚠ Failed to load cached OCR results: {e}")
        return False

    def extract_text_from_image(self, image_path: Path) -> str:
        """
        画像からテキストを抽出（キャッシュがあれば使用）

        Args:
            image_path: 画像ファイルのパス

        Returns:
            抽出されたテキスト
        """
        # キャッシュされたOCR結果があれば使用
        if self.cached_ocr_results:
            cached_text = self.cached_ocr_results.get(str(image_path))
            if cached_text is not None:
                # 日本語モードの場合、キャッシュされたテキストもクリーニング
                if self.lang == 'jpn':
                    return self.clean_japanese_spaces(cached_text)
                return cached_text

        # キャッシュがない場合はOCR実行
        try:
            # 画像を開く
            image = Image.open(image_path)

            # OCR実行
            text = pytesseract.image_to_string(image, lang=self.lang)
            text = text.strip()

            # 日本語モードの場合、不要なスペースを除去
            if self.lang == 'jpn':
                text = self.clean_japanese_spaces(text)

            return text

        except Exception as e:
            print(f"⚠ Error processing {image_path}: {e}")
            return ""

    def process_images(self, image_paths: List[Path],
                      show_progress: bool = True) -> List[str]:
        """
        複数の画像からテキストを抽出

        Args:
            image_paths: 画像ファイルのパスリスト
            show_progress: 進捗表示するかどうか

        Returns:
            各ページのテキストリスト
        """
        texts = []
        total = len(image_paths)

        for i, image_path in enumerate(image_paths, 1):
            if show_progress:
                print(f"Processing page {i}/{total}: {image_path.name}")

            text = self.extract_text_from_image(image_path)
            texts.append(text)

        return texts

    def convert_to_markdown(self, texts: List[str],
                           title: str = "Kindle Book",
                           add_page_separators: bool = True) -> str:
        """
        抽出したテキストをMarkdown形式に変換

        Args:
            texts: 各ページのテキストリスト
            title: ドキュメントのタイトル
            add_page_separators: ページ区切りを追加するかどうか

        Returns:
            Markdown形式のテキスト
        """
        markdown_lines = []

        # タイトル
        markdown_lines.append(f"# {title}\n")

        # 各ページのテキストを追加
        for i, text in enumerate(texts, 1):
            if text:  # 空でないテキストのみ追加
                if add_page_separators:
                    markdown_lines.append(f"\n---\n## Page {i}\n")

                markdown_lines.append(text)

        return "\n".join(markdown_lines)

    def save_markdown(self, markdown_text: str, output_path: Path):
        """
        Markdownテキストをファイルに保存

        Args:
            markdown_text: Markdownテキスト
            output_path: 出力ファイルのパス
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)

        print(f"✓ Markdown saved to: {output_path}")

    def process_and_save(self, image_paths: List[Path],
                        output_path: Path,
                        title: str = "Kindle Book",
                        add_page_separators: bool = True,
                        ocr_cache_dir: Optional[Path] = None) -> str:
        """
        画像からテキスト抽出→Markdown変換→保存を一括実行

        Args:
            image_paths: 画像ファイルのパスリスト
            output_path: 出力ファイルのパス
            title: ドキュメントのタイトル
            add_page_separators: ページ区切りを追加するかどうか
            ocr_cache_dir: OCRキャッシュファイルがあるディレクトリ

        Returns:
            Markdown形式のテキスト
        """
        print("\n=== OCR Processing Started ===")

        # OCRキャッシュを読み込み
        if ocr_cache_dir:
            ocr_cache_file = ocr_cache_dir / "ocr_results.json"
            self.load_cached_ocr_results(ocr_cache_file)

        # テキスト抽出
        texts = self.process_images(image_paths)

        # Markdown変換
        print("\nConverting to Markdown...")
        markdown_text = self.convert_to_markdown(
            texts,
            title=title,
            add_page_separators=add_page_separators
        )

        # 保存
        self.save_markdown(markdown_text, output_path)

        print(f"\n=== OCR Processing Complete ===")
        print(f"Total pages processed: {len(texts)}")
        print(f"Total characters: {len(markdown_text)}")

        return markdown_text


if __name__ == "__main__":
    # テスト実行
    from pathlib import Path

    processor = OCRProcessor(lang='jpn')

    # テスト用の画像パス（実際には存在するファイルを指定）
    test_images = list(Path("output").glob("*.png"))

    if test_images:
        output_file = Path("output/output.md")
        processor.process_and_save(
            test_images,
            output_file,
            title="Test Book"
        )
    else:
        print("No images found in output directory")
