#!/usr/bin/env python3
"""
自動フォーカス機能のテストスクリプト
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kindle_capture import KindleCapture


def test_auto_focus():
    """自動フォーカス機能をテスト"""
    print("=== Auto-Focus Test ===\n")

    capturer = KindleCapture(auto_focus=True, app_name="Kindle")

    print("Testing auto-focus to Kindle app...")
    if capturer.setup_window_capture():
        print("\n✓ Auto-focus successful!")
        if capturer.window_region:
            x, y, w, h = capturer.window_region
            print(f"✓ Window region detected: x={x}, y={y}, width={w}, height={h}")
        else:
            print("⚠ Window region not detected (fallback to full screen)")
    else:
        print("\n✗ Auto-focus failed")
        print("Please make sure:")
        print("  1. Kindle app is running")
        print("  2. Terminal has accessibility permissions (macOS)")

    print("\n" + "=" * 40)


if __name__ == "__main__":
    test_auto_focus()
