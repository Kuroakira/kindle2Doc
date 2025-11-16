# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kindle2MD is a Python tool that automatically captures pages from the Kindle app (or similar e-reader apps), performs OCR to extract text, and uploads the result to Google Docs as Markdown. It supports both Japanese and English books, with special handling for vertical (縦書き) Japanese text.

## Architecture

The project follows a modular, pipeline-based architecture with three main stages:

1. **Capture Stage** (`src/kindle_capture.py`):
   - Uses PyAutoGUI for keyboard automation and screenshot capture
   - macOS-specific AppleScript integration for automatic window focus and bounds detection
   - Multi-display support via window region detection
   - Intelligent end-of-book detection using image hashing (imagehash) and OCR-based text comparison
   - Page similarity detection with configurable threshold (lower = stricter)

2. **OCR Stage** (`src/ocr_processor.py`):
   - Tesseract OCR integration with language support (jpn/eng)
   - OCR result caching to avoid redundant processing during capture
   - Markdown conversion with optional page separators

3. **Upload Stage** (`src/google_docs_uploader.py`):
   - Google Docs API integration using OAuth2
   - Token persistence via `token.json`
   - Batch text insertion for efficient document creation

## Key Technical Details

### End Detection System

The capture module uses a hybrid approach for detecting the final page:
- **Image-based**: Compares perceptual hashes using imagehash library
- **OCR-based**: Extracts text during capture and compares similarity using SequenceMatcher
- Both methods can be tuned via `similarity_threshold` (0-10 range, default=2)
- Can be completely disabled with `disable_end_detection` flag

### macOS-Specific Features

- Window focus automation requires Accessibility permissions
- Uses AppleScript via `subprocess` for window management
- Window bounds detection enables multi-display support
- Falls back to full-screen capture if window detection fails

### Language Support

- OCR language configured via `--lang` flag (jpn/eng)
- Page direction affects keyboard automation: `--page-direction left` uses left arrow (縦書き), `right` uses right arrow (横書き)
- Tesseract uses `tessdata_best` models for higher accuracy

## Development Commands

### Testing

```bash
# Test auto-focus functionality (macOS only)
python test_focus.py
```

### Running the Tool

```bash
# Japanese vertical text book
python kindle2md.py --title "本のタイトル" --page-direction left

# English book
python kindle2md.py --title "Book Title" --lang eng

# Save as Markdown only (skip Google Docs upload)
python kindle2md.py --title "Book Title" --save-markdown output.md

# Keep captured images for debugging
python kindle2md.py --title "Book Title" --keep-images

# Disable automatic end detection
python kindle2md.py --title "Book Title" --disable-end-detection --max-pages 100
```

### Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Important Constraints

- **macOS Only**: Auto-focus and window detection require macOS and Accessibility permissions
- **Tesseract Required**: Must be installed via Homebrew with language data
- **Google API Credentials**: Requires OAuth credentials in `credentials/credentials.json` (see GOOGLE_SETUP.md)
- **Single-threaded**: Captures pages sequentially to avoid timing issues
- **Token Management**: `token.json` stores OAuth refresh tokens in project root (gitignored)

## Code Modification Guidelines

### When Adding Language Support

When adding support for new languages (e.g., English books):

1. **OCR Language**: The `--lang` parameter controls Tesseract language model selection. Ensure the corresponding tessdata file is installed (e.g., `eng.traineddata` for English).

2. **Text Direction**: Most languages use `--page-direction right` (left-to-right, top-to-bottom). Only Japanese vertical text requires `--page-direction left`.

3. **End Detection Tuning**: Different languages may require different `similarity_threshold` values:
   - Latin scripts (English, etc.): May need higher threshold (3-4) due to consistent character shapes
   - CJK scripts (Japanese, Chinese): Default threshold (2) usually works well
   - Test with `--disable-end-detection` first to validate OCR quality

4. **OCR Processing**: No code changes needed for language support - Tesseract handles language models via the `lang` parameter in `pytesseract.image_to_string()`.

### When Modifying Capture Logic

- The `delay` parameter controls timing between page turn and screenshot - adjust for slower devices
- OCR results are cached in `ocr_texts` dict during capture for end detection
- Image similarity uses `imagehash.phash()` with hamming distance comparison
- Text similarity uses `difflib.SequenceMatcher` with configurable threshold

### When Modifying Google Docs Integration

- Document creation and text insertion use separate API calls
- Text is inserted in batches for efficiency (see `insert_text_to_document`)
- OAuth scopes are minimal: `documents` and `drive.file` only
