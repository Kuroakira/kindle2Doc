# Kindle2Sum

Automatically capture Kindle app pages while turning pages, and generate AI-powered page summaries directly from images using Gemini Vision API. Optimized for RAG (Retrieval-Augmented Generation) data preparation.

## Features

- ✅ Automatic Kindle app page capture
- ✅ **Auto-focus (macOS)** - Automatically focuses Kindle app after command execution
- ✅ **Multi-display support** - Captures specific window only
- ✅ **Vertical/Horizontal text support** - Supports Japanese vertical writing
- ✅ Automatic end-of-book detection
- ✅ **AI summarization (Gemini Vision API)** - Reads and summarizes text directly from images
- ✅ Markdown output format
- ✅ **Google Docs upload (optional)** - Save summaries to Google Docs

## Requirements

### System Requirements

- Python 3.9 or higher
- macOS (PyAutoGUI supports macOS)
- Google Cloud account

### Google Cloud API Credentials

The following APIs are required:

1. **Google Gemini API (Required)** - AI summarization from images
   - API Key authentication required
   - See [GEMINI_SETUP.md](GEMINI_SETUP.md) for detailed setup

2. **Google Docs API (Optional)** - Document upload
   - OAuth authentication required (only if uploading to Docs)
   - See [GOOGLE_SETUP.md](GOOGLE_SETUP.md) for detailed setup

**Pricing**:
- Gemini API: Free tier (1,500 requests/day, 15M tokens/month), see [GEMINI_SETUP.md](GEMINI_SETUP.md) for details

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd kindle2md
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Google API credentials

#### Gemini API (Required - for summarization)
Follow [GEMINI_SETUP.md](GEMINI_SETUP.md) to obtain and configure API Key:

**Method 1: Environment variable (recommended)**
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

**Method 2: .env file**
```bash
echo "GEMINI_API_KEY=your-gemini-api-key" > .env
```

#### Google Docs API (Optional - for upload)
Only required if uploading summaries to Google Docs.
Follow [GOOGLE_SETUP.md](GOOGLE_SETUP.md) to obtain and place OAuth credentials:

```bash
mkdir -p credentials
mv ~/Downloads/credentials.json credentials/
```

### 5. Recommended Kindle settings (for better accuracy)

Configure the following settings in Kindle app:

1. **Font size**: As large as possible
2. **Window size**: Fullscreen or maximized
3. **Brightness**: Bright setting
4. **Margins**: Reduce margins if possible

These settings significantly improve Gemini Vision API recognition accuracy.

## Usage

### Pre-check (Recommended)

To verify auto-focus functionality works correctly:

```bash
source venv/bin/activate
python test_focus.py
```

### Basic Usage

1. Open Kindle app and display the first page of the book you want to summarize
2. Run the following command in terminal

```bash
source venv/bin/activate

# Set environment variable (if not using .env file)
export GEMINI_API_KEY="your-gemini-api-key"

# Horizontal text book (default)
# Note: No export needed if you created .env file
python kindle2sum.py --title "Book Title" --save-summary summary.md

# Vertical text book (many Japanese books)
python kindle2sum.py --title "Book Title" --page-direction left --save-summary summary.md

# Also upload summary to Google Docs
python kindle2sum.py --title "Book Title" --save-summary summary.md --upload-to-docs
```

3. **Kindle app will be automatically focused** (macOS only)
4. Capture starts automatically after 2 seconds
5. Automatically captures until the last page and generates summaries with Gemini Vision API

**Important**: For Japanese vertical text books, specify `--page-direction left` (uses left arrow key for page turning).

### Options

```bash
# Specify title
python kindle2sum.py --title "My Book" --save-summary output.md

# Change page turn delay (default: 1.5 seconds)
python kindle2sum.py --title "My Book" --delay 2.0 --save-summary output.md

# Keep captured images (deleted by default)
python kindle2sum.py --title "My Book" --keep-images --save-summary output.md

# Disable auto-focus (for manual focusing)
python kindle2sum.py --title "My Book" --no-auto-focus --save-summary output.md

# Capture different app (e.g., Kobo)
python kindle2sum.py --title "My Book" --app-name "Kobo" --save-summary output.md

# Vertical text book (left arrow for page turn)
python kindle2sum.py --title "Japanese Book" --page-direction left --save-summary output.md

# Change Gemini model
python kindle2sum.py --title "My Book" --gemini-model gemini-2.5-pro --save-summary output.md

# Test run with 3 pages only
python kindle2sum.py --title "Test" --max-pages 3 --save-summary test.md
```

### All Options

| Option | Description | Default |
|--------|-------------|---------|
| `--title` | Document title | `Kindle Book` |
| `--output-dir` | Capture image directory | `output` |
| `--delay` | Delay after page turn (seconds) | `1.5` |
| `--max-pages` | Maximum number of pages | `1000` |
| `--page-direction` | Page turn direction (`left`=vertical, `right`=horizontal) | `right` |
| `--save-summary` | Summary Markdown file path | None (required) |
| `--upload-to-docs` | Also upload to Google Docs | `False` |
| `--keep-images` | Keep captured images | `False` |
| `--no-auto-focus` | Disable auto-focus | `False` |
| `--app-name` | App name to capture | `Kindle` |
| `--gemini-model` | Gemini model to use | `gemini-2.5-flash` |
| `--similarity-threshold` | End detection threshold (0-10) | `2` |
| `--disable-end-detection` | Disable automatic end detection | `False` |

## Output Format

Generated summary Markdown file format:

```markdown
# Book Title
**Total pages**: 100
**Generation method**: Gemini Vision API (direct image summarization)
**Summary format**: Bullet points (RAG optimized)

---
<!-- Page: 1 -->

- Author's experience struggling to sell products during sales internship
- Realization that knowing about PMF (Product-Market Fit) concept would have saved wasted effort
- Motivation to spread awareness of PMF importance based on current success
- Goal to support people in new ventures to direct their efforts correctly

---
<!-- Page: 2 -->

- Basic definition and importance of PMF
- Methods to identify market-product fit
- Differences in business before and after achieving PMF

...
```

### Removing Metadata for RAG (Retrieval-Augmented Generation)

When using summaries for vector embeddings or RAG systems, you can easily remove metadata like page numbers using regular expressions:

```python
import re

# Load Markdown file
with open('summary.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove HTML comments (page numbers, image paths)
content_without_metadata = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

# Also remove separators if desired
content_clean = re.sub(r'\n---\n', '\n', content_without_metadata)
```

## Project Structure

```
kindle2md/
├── kindle2sum.py          # Main script
├── src/
│   ├── kindle_capture.py  # Kindle capture module
│   ├── summarizer.py      # AI summarization module (Gemini Vision API)
│   └── google_docs_uploader.py  # Google Docs upload module
├── credentials/           # Google API credentials (.gitignore)
│   └── credentials.json   # Google Docs API credentials (optional)
├── output/                # Temporary files (.gitignore)
├── requirements.txt       # Dependencies
├── GEMINI_SETUP.md       # Google Gemini API setup guide
├── GOOGLE_SETUP.md       # Google Docs API setup guide (optional)
└── README.md             # This file
```

## Troubleshooting

### Auto-focus not working

**For macOS:**
Accessibility permission may be required in System Preferences.

1. System Preferences > Security & Privacy > Privacy > Accessibility
2. Check Terminal or iTerm2

**Workaround:**
Use `--no-auto-focus` option for manual focusing:

```bash
python kindle2sum.py --title "Book Title" --no-auto-focus --save-summary output.md
```

### Full screen captured on multi-display

When auto-focus is enabled, only the Kindle window should be captured.
If full screen is captured, the Kindle app may not be recognized correctly.

**Solution:**
- Verify Kindle app is running
- Specify exact app name with `--app-name` option

### Gemini API authentication error

```
API key not configured
```

Verify that `GEMINI_API_KEY` environment variable is set:

```bash
echo $GEMINI_API_KEY
# Should display your API Key
```

See [GEMINI_SETUP.md](GEMINI_SETUP.md) for details.

### Google Docs API authentication error

Verify that `credentials/credentials.json` is correctly placed. See [GOOGLE_SETUP.md](GOOGLE_SETUP.md) for details.

### Low summary accuracy

- Try increasing page turn delay with `--delay` option (prevents image blur)
- Increasing Kindle app display size may improve recognition accuracy
- Increasing font size improves Gemini Vision API recognition accuracy

### Improve summary quality

- Use `--gemini-model gemini-2.5-pro` for higher quality (complex reasoning tasks)
- Use `--gemini-model gemini-2.5-flash-lite` for faster/lower cost
- Note: Pro model is more expensive

### Capture won't stop

End detection may have failed. Interrupt with `Ctrl+C`.

## Important Notes

- This tool is intended for personal use
- Please comply with copyright laws
- **Do not operate mouse or keyboard during capture**
- Auto-focus feature unavailable on non-macOS systems
- Monitor API usage (charges apply when exceeding free tier)

## License

MIT License

## Contributing

Bug reports and feature requests welcome via Issues.
