"""
Kindleアプリのページキャプチャモジュール
"""
import time
import pyautogui
from PIL import Image
import imagehash
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import subprocess
import platform
import pytesseract
import json
from difflib import SequenceMatcher


class KindleCapture:
    """Kindleアプリのページを自動でキャプチャするクラス"""

    def __init__(self, output_dir: str = "output", delay: float = 1.5,
                 auto_focus: bool = True, app_name: str = "Kindle",
                 page_direction: str = "right", similarity_threshold: int = 2,
                 disable_end_detection: bool = False, ocr_lang: str = "jpn",
                 use_ocr_detection: bool = True):
        """
        Args:
            output_dir: キャプチャ画像の保存先ディレクトリ
            delay: ページ送り後の待機時間（秒）
            auto_focus: Kindleアプリに自動でフォーカスするか
            app_name: キャプチャするアプリ名（デフォルト: Kindle）
            page_direction: ページ送りの方向（'left'=左矢印/縦書き, 'right'=右矢印/横書き）
            similarity_threshold: 最終ページ検出の閾値（小さいほど厳格、0で最も厳格）
            disable_end_detection: 最終ページ自動検出を無効化
            ocr_lang: OCR言語（'jpn'=日本語, 'eng'=英語）
            use_ocr_detection: OCRベースの終了検出を使用
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.delay = delay
        self.auto_focus = auto_focus
        self.app_name = app_name
        self.page_direction = page_direction
        self.similarity_threshold = similarity_threshold
        self.disable_end_detection = disable_end_detection
        self.ocr_lang = ocr_lang
        self.use_ocr_detection = use_ocr_detection
        self.captured_images: List[Path] = []
        self.window_region: Optional[Tuple[int, int, int, int]] = None
        self.ocr_texts: Dict[str, str] = {}  # 画像パス -> OCRテキスト

    def focus_app_macos(self) -> bool:
        """
        macOSでKindleアプリにフォーカスを当てる

        Returns:
            成功した場合True
        """
        try:
            # System Eventsを使ってプロセスをフォーカス（より確実な方法）
            script = f'tell application "System Events" to tell process "{self.app_name}" to set frontmost to true'
            subprocess.run(['osascript', '-e', script],
                         check=True,
                         capture_output=True,
                         timeout=5)
            time.sleep(1.0)  # フォーカス切り替えの待機（マルチディスプレイ対応のため長めに）
            print(f"✓ Focused on {self.app_name} app")
            return True
        except subprocess.CalledProcessError as e:
            # text=Trueを指定しているので、stderrは既に文字列
            stderr = e.stderr if e.stderr else ''
            print(f"⚠ Failed to focus {self.app_name}: {stderr}")
            return False
        except subprocess.TimeoutExpired:
            print(f"⚠ Timeout focusing {self.app_name}")
            return False

    def get_window_bounds_macos(self) -> Optional[Tuple[int, int, int, int]]:
        """
        macOSでKindleアプリウィンドウの境界を取得

        Returns:
            (x, y, width, height) または None
        """
        try:
            # ウィンドウの位置を取得
            pos_script = f'tell application "System Events" to tell process "{self.app_name}" to get position of window 1'
            pos_result = subprocess.run(['osascript', '-e', pos_script],
                                      check=True,
                                      capture_output=True,
                                      text=True,
                                      timeout=5)

            # ウィンドウのサイズを取得
            size_script = f'tell application "System Events" to tell process "{self.app_name}" to get size of window 1'
            size_result = subprocess.run(['osascript', '-e', size_script],
                                       check=True,
                                       capture_output=True,
                                       text=True,
                                       timeout=5)

            # 出力をパース
            pos = pos_result.stdout.strip().split(', ')
            size = size_result.stdout.strip().split(', ')

            x, y = int(pos[0]), int(pos[1])
            width, height = int(size[0]), int(size[1])

            print(f"✓ Window bounds: x={x}, y={y}, w={width}, h={height}")
            return (x, y, width, height)

        except subprocess.CalledProcessError as e:
            # text=Trueを指定しているので、stderrは既に文字列
            stderr = e.stderr if e.stderr else ''
            print(f"⚠ Could not get window bounds: {stderr}")
        except Exception as e:
            print(f"⚠ Could not get window bounds: {e}")

        return None

    def setup_window_capture(self):
        """ウィンドウキャプチャの準備（フォーカス+境界取得）"""
        if platform.system() != "Darwin":
            print("⚠ Auto-focus only supported on macOS")
            return False

        if self.auto_focus:
            # アプリにフォーカス
            if not self.focus_app_macos():
                return False

            # ウィンドウの境界を取得
            self.window_region = self.get_window_bounds_macos()

        return True

    def capture_screenshot(self, page_num: int) -> Path:
        """
        現在の画面をキャプチャして保存

        Args:
            page_num: ページ番号

        Returns:
            保存した画像のパス
        """
        # スクリーンショットを撮影
        if self.window_region:
            # 特定のウィンドウ領域のみキャプチャ（マルチディスプレイ対応）
            x, y, width, height = self.window_region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            # 全画面キャプチャ
            screenshot = pyautogui.screenshot()

        # ファイル名を生成
        filename = self.output_dir / f"page_{page_num:04d}.png"

        # 保存
        screenshot.save(filename)
        print(f"✓ Page {page_num} captured: {filename}")

        return filename

    def next_page(self):
        """矢印キーでページを送る（縦書き=left, 横書き=right）"""
        pyautogui.press(self.page_direction)
        time.sleep(self.delay)

    def ocr_image(self, image_path: Path) -> str:
        """
        画像からテキストを抽出（OCR）

        Args:
            image_path: 画像ファイルのパス

        Returns:
            抽出されたテキスト
        """
        try:
            with Image.open(image_path) as img:
                text = pytesseract.image_to_string(img, lang=self.ocr_lang)
                return text.strip()
        except Exception as e:
            print(f"  ⚠ OCR error: {e}")
            return ""

    def text_similarity(self, text1: str, text2: str) -> float:
        """
        2つのテキストの類似度を計算（0.0-1.0）

        Args:
            text1: テキスト1
            text2: テキスト2

        Returns:
            類似度（0.0=全く違う, 1.0=完全一致）
        """
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1, text2).ratio()

    def calculate_image_hash(self, image_path: Path) -> imagehash.ImageHash:
        """
        画像のハッシュ値を計算

        Args:
            image_path: 画像ファイルのパス

        Returns:
            画像のハッシュ値
        """
        with Image.open(image_path) as img:
            return imagehash.average_hash(img)

    def is_last_page(self, current_hash: imagehash.ImageHash,
                     previous_hash: imagehash.ImageHash) -> bool:
        """
        現在のページが最終ページかどうかを判定
        （前のページと同じ画像が表示されているか）

        Args:
            current_hash: 現在のページのハッシュ値
            previous_hash: 前のページのハッシュ値

        Returns:
            最終ページの場合True
        """
        if self.disable_end_detection:
            return False

        diff = current_hash - previous_hash
        is_same = diff <= self.similarity_threshold

        if is_same:
            print(f"  Similar pages detected (diff={diff}, threshold={self.similarity_threshold})")

        return is_same

    def capture_all_pages(self, max_pages: int = 1000) -> List[Path]:
        """
        Kindleの全ページをキャプチャ

        Args:
            max_pages: 最大ページ数（無限ループ防止）

        Returns:
            キャプチャした画像ファイルのパスリスト
        """
        print("=== Kindle Page Capture Started ===")
        print(f"Output directory: {self.output_dir}")
        print(f"Delay between pages: {self.delay}s")

        # 自動フォーカス設定
        if self.auto_focus:
            print(f"\nAttempting to auto-focus {self.app_name} app...")
            if not self.setup_window_capture():
                print("⚠ Auto-focus failed. Please manually focus the Kindle app.")
                print("Starting in 5 seconds...")
                time.sleep(5)
            else:
                print("Starting in 2 seconds...")
                time.sleep(2)
        else:
            print(f"\nMake sure {self.app_name} app is in focus!")
            print("Starting in 3 seconds...")
            time.sleep(3)

        previous_hash = None
        previous_text = None
        page_num = 1

        # OCRベースの検出を使用するか
        use_ocr = self.use_ocr_detection and not self.disable_end_detection

        if use_ocr:
            print("Using OCR-based end detection for better accuracy")

        while page_num <= max_pages:
            # スクリーンショットを撮影
            image_path = self.capture_screenshot(page_num)
            self.captured_images.append(image_path)

            # OCRベースの終了検出
            if use_ocr:
                # OCR実行
                print(f"  Running OCR on page {page_num}...", end=" ")
                current_text = self.ocr_image(image_path)
                self.ocr_texts[str(image_path)] = current_text
                print(f"({len(current_text)} chars)")

                # 2ページ目以降で類似度をチェック
                if previous_text is not None and len(current_text) > 50:
                    similarity = self.text_similarity(previous_text, current_text)
                    if similarity > 0.95:  # 95%以上同じ
                        print(f"\n✓ Last page detected (text similarity: {similarity:.2%})")
                        # 重複した最後のページを削除
                        image_path.unlink()
                        self.captured_images.pop()
                        del self.ocr_texts[str(image_path)]
                        break

                previous_text = current_text

            # 画像ハッシュベースのフォールバック検出
            else:
                current_hash = self.calculate_image_hash(image_path)

                # 最終ページチェック（2ページ目以降）
                if previous_hash is not None:
                    if self.is_last_page(current_hash, previous_hash):
                        print(f"\n✓ Last page detected at page {page_num}")
                        # 重複した最後のページを削除
                        image_path.unlink()
                        self.captured_images.pop()
                        break

                previous_hash = current_hash

            # 次のページへ
            if page_num < max_pages:
                self.next_page()

            page_num += 1

        print(f"\n=== Capture Complete ===")
        print(f"Total pages captured: {len(self.captured_images)}")

        # OCR結果を保存
        if use_ocr and self.ocr_texts:
            self.save_ocr_texts()

        return self.captured_images

    def save_ocr_texts(self):
        """OCR結果をJSONファイルに保存"""
        ocr_file = self.output_dir / "ocr_results.json"
        with open(ocr_file, 'w', encoding='utf-8') as f:
            json.dump(self.ocr_texts, f, ensure_ascii=False, indent=2)
        print(f"✓ OCR results saved to: {ocr_file}")

    def cleanup(self):
        """一時ファイルをクリーンアップ"""
        for image_path in self.captured_images:
            if image_path.exists():
                image_path.unlink()
        self.captured_images.clear()
        print("✓ Temporary files cleaned up")


if __name__ == "__main__":
    # テスト実行
    capturer = KindleCapture()
    try:
        images = capturer.capture_all_pages(max_pages=10)
        print(f"\nCaptured images: {len(images)}")
    except KeyboardInterrupt:
        print("\n\nCapture interrupted by user")
    finally:
        # クリーンアップは手動で実行
        # capturer.cleanup()
        pass
