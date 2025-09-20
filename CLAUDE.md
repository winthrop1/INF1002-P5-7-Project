# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a phishing email detection system built with Python and Flask. The application analyzes email content to detect potential phishing attempts using keyword-based scoring.

## Architecture

### Core Components

1. **detector.py**: Main detection logic that classifies emails as "Safe" or "Phishing"
   - Loads spam keywords from `words/spam_words.txt`
   - Scores keywords differently based on location (subject vs body)
   - Subject keywords: 3 points each
   - Body keywords: 1 point each
   - Classification: Score > 0 = Phishing, Score = 0 = Safe

2. **spamwords.py**: Web scraper for obtaining spam keywords
   - Scrapes keywords from activecampaign.com
   - Filters phrases to 5 words or less
   - Saves to `words/spam_words.txt`

3. **website.py**: Flask web application
   - Provides upload interface for email files (.eml, .txt)
   - Displays classification results with risk score
   - Template folder: `website/`

4. **website/index.html**: Bootstrap-based UI for email upload and analysis

### Data Structure

- **ham/**: Sample legitimate email files (ham_1.txt through ham_12.txt)
- **spam/**: Sample phishing email files (spam_1.txt through spam_12.txt)
- **words/spam_words.txt**: List of spam keywords used for detection

## Development Commands

### Running the Web Application
```bash
python website.py
```
The application will run on http://127.0.0.1:5000 with debug mode enabled.

### Testing Email Classification
```python
from detector import classify_email
classification, keywords, score = classify_email(email_text)
```

### Updating Spam Keywords
```bash
python spamwords.py
```

## Important Path Configurations

The code contains hardcoded paths that need adjustment for different systems:
- **detector.py:34**: Update `txt_path` to match your local path
- **spamwords.py:8**: Update `output_folder` to match your local path

## Dependencies

Install all dependencies:
```bash
py -m pip install -r requirements.txt
```

Required packages:
- Flask (for web application)
- requests (for web scraping)
- lxml (for HTML parsing)
- python-dotenv (for environment variables)
- Standard library: re, os