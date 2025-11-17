#!/usr/bin/env python3
"""
Kindle2Sum - Kindleアプリを自動キャプチャしてページ要約を生成

Usage:
    python kindle2sum.py --title "Book Title" [options]
"""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kindle_capture import KindleCapture
from summarizer import Summarizer
from google_docs_uploader import GoogleDocsUploader


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='Kindle2Sum - Kindleアプリを自動キャプチャしてページ要約を生成'
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
        '--keep-images',
        action='store_true',
        help='キャプチャ画像を削除せずに保持'
    )
    parser.add_argument(
        '--save-summary',
        type=str,
        help='要約Markdownファイルを指定パスに保存'
    )
    parser.add_argument(
        '--upload-to-docs',
        action='store_true',
        help='要約をGoogle Docsにもアップロード'
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
    parser.add_argument(
        '--gemini-model',
        type=str,
        default='gemini-2.5-flash',
        help='使用するGeminiモデル（デフォルト: gemini-2.5-flash）'
    )

    args = parser.parse_args()

    try:
        print("=" * 60)
        print("  Kindle2Sum - Kindle to Summary Generator")
        print("=" * 60)

        # ステップ1: Kindleキャプチャ
        print("\n[Step 1/4] Capturing Kindle pages...")
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

        # ステップ2: 要約生成（Gemini Visionで画像から直接）
        print("\n[Step 2/3] Generating summaries with Gemini Vision API...")
        summarizer = Summarizer(model_name=args.gemini_model)

        summary_output = Path(args.output_dir) / "summary.md"
        summary_text = summarizer.process_and_save(
            image_paths,
            summary_output,
            title=args.title
        )

        # 指定パスに保存
        if args.save_summary:
            save_path = Path(args.save_summary)
            summarizer.save_summary_markdown(summary_text, save_path)
            print(f"\n✓ Summary saved to: {save_path}")

        # ステップ3: Google Docsアップロード（オプション）
        if args.upload_to_docs:
            print("\n[Step 3/3] Uploading to Google Docs...")
            uploader = GoogleDocsUploader()
            doc_url = uploader.upload_markdown(summary_text, title=f"{args.title} - Summary")
            print(f"\n✓ Google Docs URL: {doc_url}")

        # クリーンアップ
        if not args.keep_images:
            print("\nCleaning up temporary files...")
            capturer.cleanup()
            summary_output.unlink(missing_ok=True)

        print("\n" + "=" * 60)
        print("  Complete!")
        print("=" * 60)
        print(f"\n✓ Total pages: {len(image_paths)}")
        print(f"✓ Title: {args.title}")
        if args.save_summary:
            print(f"✓ Summary: {args.save_summary}")

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
