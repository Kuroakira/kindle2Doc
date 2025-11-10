#!/usr/bin/env python3
"""
Kindle2MD - Kindleアプリを自動キャプチャしてGoogle Docsにアップロード

Usage:
    python kindle2md.py --title "Book Title" [options]
"""
import argparse
import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kindle_capture import KindleCapture
from ocr_processor import OCRProcessor
from google_docs_uploader import GoogleDocsUploader


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='Kindle2MD - Kindleアプリを自動キャプチャしてGoogle Docsにアップロード'
    )
    parser.add_argument(
        '--title',
        type=str,
        default='Kindle Book',
        help='ドキュメントのタイトル（デフォルト: Kindle Book）'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='キャプチャ画像の一時保存先（デフォルト: output）'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.5,
        help='ページ送り後の待機時間（秒）（デフォルト: 1.5）'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=1000,
        help='最大ページ数（デフォルト: 1000）'
    )
    parser.add_argument(
        '--lang',
        type=str,
        default='jpn',
        help='OCR言語（jpn=日本語, eng=英語）（デフォルト: jpn）'
    )
    parser.add_argument(
        '--no-page-separators',
        action='store_true',
        help='Markdownにページ区切りを追加しない'
    )
    parser.add_argument(
        '--keep-images',
        action='store_true',
        help='キャプチャ画像を削除せずに保持'
    )
    parser.add_argument(
        '--save-markdown',
        type=str,
        help='Markdownファイルを指定パスに保存（Google Docsへのアップロードなし）'
    )
    parser.add_argument(
        '--no-auto-focus',
        action='store_true',
        help='アプリへの自動フォーカスを無効化（macOSのみ）'
    )
    parser.add_argument(
        '--app-name',
        type=str,
        default='Kindle',
        help='キャプチャするアプリ名（デフォルト: Kindle）'
    )
    parser.add_argument(
        '--page-direction',
        type=str,
        choices=['left', 'right'],
        default='right',
        help='ページ送りの方向（left=左矢印/縦書き, right=右矢印/横書き）（デフォルト: right）'
    )
    parser.add_argument(
        '--similarity-threshold',
        type=int,
        default=2,
        help='最終ページ検出の閾値（0-10、小さいほど厳格）（デフォルト: 2）'
    )
    parser.add_argument(
        '--disable-end-detection',
        action='store_true',
        help='最終ページ自動検出を無効化（max-pagesまでキャプチャ）'
    )

    args = parser.parse_args()

    try:
        print("=" * 60)
        print("  Kindle2MD - Kindle to Google Docs Converter")
        print("=" * 60)

        # ステップ1: Kindleキャプチャ
        print("\n[Step 1/3] Capturing Kindle pages...")
        capturer = KindleCapture(
            output_dir=args.output_dir,
            delay=args.delay,
            auto_focus=not args.no_auto_focus,
            app_name=args.app_name,
            page_direction=args.page_direction,
            similarity_threshold=args.similarity_threshold,
            disable_end_detection=args.disable_end_detection,
            ocr_lang=args.lang
        )
        image_paths = capturer.capture_all_pages(max_pages=args.max_pages)

        if not image_paths:
            print("⚠ No pages captured. Exiting.")
            return

        # ステップ2: OCR処理
        print("\n[Step 2/3] Processing OCR and converting to Markdown...")
        processor = OCRProcessor(lang=args.lang)

        markdown_output = Path(args.output_dir) / "output.md"
        markdown_text = processor.process_and_save(
            image_paths,
            markdown_output,
            title=args.title,
            add_page_separators=not args.no_page_separators,
            ocr_cache_dir=Path(args.output_dir)
        )

        # Markdownファイルを保存して終了する場合
        if args.save_markdown:
            save_path = Path(args.save_markdown)
            processor.save_markdown(markdown_text, save_path)
            print(f"\n✓ Markdown saved to: {save_path}")

            # クリーンアップ
            if not args.keep_images:
                capturer.cleanup()
                markdown_output.unlink(missing_ok=True)

            print("\n" + "=" * 60)
            print("  Complete!")
            print("=" * 60)
            return

        # ステップ3: Google Docsアップロード
        print("\n[Step 3/3] Uploading to Google Docs...")
        uploader = GoogleDocsUploader()
        doc_url = uploader.upload_markdown(markdown_text, title=args.title)

        # クリーンアップ
        if not args.keep_images:
            print("\nCleaning up temporary files...")
            capturer.cleanup()
            markdown_output.unlink(missing_ok=True)

        print("\n" + "=" * 60)
        print("  Complete!")
        print("=" * 60)
        print(f"\n✓ Google Docs URL: {doc_url}")
        print(f"✓ Total pages: {len(image_paths)}")
        print(f"✓ Title: {args.title}")

    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
