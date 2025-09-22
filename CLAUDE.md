# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

INF1002-P5-7-Project: A phishing email detection system built with Python and Flask for the INF1002 Programming Fundamentals course. The application analyzes email content to detect potential phishing attempts using keyword-based scoring algorithms.

## Architecture

### Core Components

1. **detector.py**: Main detection logic that classifies emails as "Safe" or "Phishing"
   - Loads spam keywords from `words/spam_words.txt`
   - Implements weighted scoring system:
     - Subject keywords: 3 points each (higher weight due to importance)
     - Body keywords: 1 point each
   - Classification threshold: Score > 0 = Phishing, Score = 0 = Safe
   - Returns tuple: (classification, found_keywords, total_score)
   - Uses environment variables via python-dotenv for configuration

2. **spamwords.py**: Web scraper for maintaining spam keyword database
   - Scrapes keywords from activecampaign.com's spam words list
   - Filters phrases to maximum 5 words for better matching
   - Automatically saves to `words/spam_words.txt`
   - Can be run independently to update keyword database

3. **website.py**: Flask web application server
   - Provides file upload interface for email analysis
   - Supported file formats: .eml, .txt
   - Displays classification results with:
     - Risk level (Safe/Phishing)
     - Total risk score
     - List of detected keywords
   - Template folder: `website/`
   - Runs in debug mode for development

4. **website/index.html**: Frontend user interface
   - Bootstrap-based responsive design
   - File upload form with validation
   - Results display with color coding (green for safe, red for phishing)
   - Clean, user-friendly interface

5. **website/style.css**: Custom CSS styling
   - Additional styling on top of Bootstrap
   - Custom color schemes and layouts

### Data Structure

- **ham/**: Sample legitimate email files
  - Contains ham_1.txt through ham_12.txt
  - Used for testing false positive rates

- **spam/**: Sample phishing email files
  - Contains spam_1.txt through spam_12.txt
  - Used for testing detection accuracy

- **words/**: Keyword database directory
  - `spam_words.txt`: Master list of spam/phishing keywords

- **.env**: Environment configuration (create from .env.example)
  - `SPAM_WORDS_PATH`: Path to spam words file
  - `OUTPUT_FOLDER`: Directory for saving scraped keywords
  - `SPAM_SOURCE_URL`: URL for keyword scraping
  - `TEMPLATE_FOLDER`: Flask template directory

## Development Commands

### Initial Setup
```bash
# Clone repository
git clone [repository-url]
cd INF1002-P5-7-Project

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
cp .env.example .env
# Edit .env with your local paths if needed
```

### Running the Web Application
```bash
python website.py
```
The application will run on http://127.0.0.1:5000 with debug mode enabled.

### Testing Email Classification
```python
from detector import classify_email

# Test with a sample email
email_text = "Subject: Win $1000 now!\nClick here for free money..."
classification, keywords, score = classify_email(email_text)
print(f"Classification: {classification}")
print(f"Score: {score}")
print(f"Keywords found: {keywords}")
```

### Updating Spam Keywords Database
```bash
python spamwords.py
```
This will scrape the latest spam keywords and update `words/spam_words.txt`.

### Testing with Sample Data
```bash
# Test with legitimate emails
python detector.py ham/ham_1.txt

# Test with phishing emails
python detector.py spam/spam_1.txt
```

## Environment Configuration

The project uses environment variables for configuration. Copy `.env.example` to `.env` and update as needed:

```bash
SPAM_WORDS_PATH=words/spam_words.txt
OUTPUT_FOLDER=words
SPAM_SOURCE_URL=https://www.activecampaign.com/blog/spam-words
TEMPLATE_FOLDER=website
```

Note: The code now uses environment variables instead of hardcoded paths, making it portable across different systems.

## Dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- **flask==3.1.2**: Web framework for the application
- **requests==2.32.5**: HTTP library for web scraping
- **lxml==6.0.1**: XML/HTML processing for parsing scraped content
- **python-dotenv==1.1.1**: Environment variable management

Standard library modules used:
- **re**: Regular expressions for text processing
- **os**: File system operations
- **email.parser**: For parsing .eml files

## Code Style and Conventions

- Python 3.x compatible
- PEP 8 style guidelines
- Functions use descriptive names with docstrings
- Error handling for file operations
- Environment-based configuration over hardcoded paths

## Testing and Validation

The project includes sample data for testing:
- Use ham/ directory files to test for false positives
- Use spam/ directory files to test detection accuracy
- The scoring system can be tuned by adjusting weights in detector.py

## Known Issues

- The main guard in detector.py line 98 has incorrect syntax (`__classify_email__` should be `__main__`)
- This prevents running detector.py directly as a script with command-line arguments