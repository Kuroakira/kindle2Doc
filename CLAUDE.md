# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kindle2Sum is a Python tool that automatically captures pages from the Kindle app (or similar e-reader apps) and generates AI-powered page summaries using Gemini Vision API directly from images. It outputs Markdown format optimized for RAG (Retrieval-Augmented Generation) applications. Supports both Japanese and English books, with special handling for vertical (縦書き) Japanese text.

## Architecture

The project follows a modular, pipeline-based architecture with three main stages:

1. **Capture Stage** (`src/kindle_capture.py`):
   - Uses PyAutoGUI for keyboard automation and screenshot capture
   - macOS-specific AppleScript integration for automatic window focus and bounds detection
   - Multi-display support via window region detection
   - Intelligent end-of-book detection using image hashing (imagehash) and Tesseract OCR-based text comparison
   - Page similarity detection with configurable threshold (lower = stricter)

2. **Summarization Stage** (`src/summarizer.py`):
   - Gemini Vision API integration for direct image-to-summary processing
   - Reads text directly from images without separate OCR step
   - Page-by-page summarization (200-300 characters per page)
   - Model selection support (gemini-2.5-flash, gemini-2.5-pro, gemini-2.5-flash-lite)
   - Markdown output optimized for RAG use cases

3. **Upload Stage (Optional)** (`src/google_docs_uploader.py`):
   - Google Docs API integration using OAuth2
   - Token persistence via `token.json`
   - Batch text insertion for efficient document creation
   - Uploads generated summaries to Google Docs

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

- Gemini Vision API automatically detects and reads text from images in any language
- Page direction affects keyboard automation: `--page-direction left` uses left arrow (縦書き), `right` uses right arrow (横書き)
- Summarization prompt is currently optimized for Japanese (requests summaries in Japanese)
- For other languages, modify the prompt in `summarizer.py`

### AI Summarization (Gemini Vision)

- Uses Gemini Vision API for direct image-to-summary processing (no separate OCR step)
- Default model: `gemini-2.5-flash` (balanced performance and cost)
- Alternatives: `gemini-2.5-pro` (complex reasoning), `gemini-2.5-flash-lite` (high-speed/low-cost)
- Each page is summarized to 200-300 characters based on image content
- Markdown output format with generation method metadata

## Development Commands

### Testing

```bash
# Test auto-focus functionality (macOS only)
python test_focus.py
```

### Running the Tool

```bash
# Japanese vertical text book with AI summarization
python kindle2sum.py --title "本のタイトル" --page-direction left --save-summary output.md

# English book (Gemini Vision auto-detects language)
python kindle2sum.py --title "Book Title" --save-summary output.md

# Save summary and upload to Google Docs
python kindle2sum.py --title "Book Title" --save-summary output.md --upload-to-docs

# Keep captured images for debugging
python kindle2sum.py --title "Book Title" --keep-images --save-summary output.md

# Disable automatic end detection
python kindle2sum.py --title "Book Title" --disable-end-detection --max-pages 100 --save-summary output.md

# Use high-quality Gemini model
python kindle2sum.py --title "Book Title" --gemini-model gemini-2.5-pro --save-summary output.md
```

### Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up Gemini API key
export GEMINI_API_KEY="your-gemini-api-key-here"
```

## Important Constraints

- **macOS Only**: Auto-focus and window detection require macOS and Accessibility permissions
- **Tesseract OCR**: Required for end-of-book detection (installed via Homebrew)
- **Google Gemini API (Required)**: Requires API key via environment variable `GEMINI_API_KEY` (see GEMINI_SETUP.md)
- **Google Docs API (Optional)**: Requires OAuth credentials in `credentials/credentials.json` (see GOOGLE_SETUP.md)
- **Single-threaded**: Captures pages sequentially to avoid timing issues
- **Token Management**: `token.json` stores OAuth refresh tokens in project root (gitignored)
- **API Costs**: Gemini API free tier (1,500 requests/day, 15M tokens/month), then $0.075 per 1M tokens (Flash) or $1.25 per 1M tokens (Pro)

## Code Modification Guidelines

### When Adding Language Support

When adding support for new languages:

1. **Summarization Prompts**: The summarization prompt in `summarizer.py` is currently optimized for Japanese (requests summaries in Japanese).
   - For other languages, modify the prompt in `summarize_page_from_image()` method to request summaries in the target language

2. **Text Direction**: Most languages use `--page-direction right` (left-to-right, top-to-bottom). Only Japanese vertical text requires `--page-direction left`.

3. **End Detection Tuning**: Different languages may require different `similarity_threshold` values:
   - Latin scripts (English, etc.): May need higher threshold (3-4) due to consistent character shapes
   - CJK scripts (Japanese, Chinese): Default threshold (2) usually works well
   - Test with `--disable-end-detection` first to validate detection accuracy

4. **Gemini Vision**: No code changes needed for basic language support - Gemini Vision automatically detects and reads text from images in any language.

### When Modifying Capture Logic

- The `delay` parameter controls timing between page turn and screenshot - adjust for slower devices
- Tesseract OCR results are cached in `ocr_texts` dict during capture for end-of-book detection
- Image similarity uses `imagehash.phash()` with hamming distance comparison
- Text similarity uses `difflib.SequenceMatcher` with configurable threshold

### When Modifying Summarization

- Prompt engineering in `summarizer.py` affects summary quality, length, and output language
- Model selection impacts cost and quality: `gemini-2.5-flash` (balanced), `gemini-2.5-pro` (complex reasoning), `gemini-2.5-flash-lite` (high-speed)
- Summary length is configurable in the prompt (currently 200-300 characters)
- The method `summarize_page_from_image()` takes image paths directly and uses Gemini Vision multimodal capabilities
- Markdown output format is generated in `create_summary_markdown()` method

### When Modifying Google Docs Integration

- Document creation and text insertion use separate API calls
- Text is inserted in batches for efficiency (see `insert_text_to_document`)
- OAuth scopes are minimal: `documents` and `drive.file` only
- Google Docs upload is now optional via `--upload-to-docs` flag
