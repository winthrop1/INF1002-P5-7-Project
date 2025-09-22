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
   - Imports domain list from datas.py for domain checking
   - `domaincheck()` function: Checks if sender domain is in known spam domains list

2. **spamwords.py**: Web scraper for maintaining spam keyword database
   - Scrapes keywords from activecampaign.com's spam words list
   - Filters phrases to maximum 5 words for better matching
   - Automatically saves to `words/spam_words.txt`
   - Can be run independently to update keyword database

3. **website.py**: Flask web application server
   - Provides file upload interface for email analysis
   - Supported file formats: .eml, .txt
   - Email functionality:
     - Sends analysis report to user's email address
     - Uses SMTP with Gmail for email delivery
   - Displays classification results with:
     - Risk level (Safe/Phishing)
     - Total risk score
     - List of detected keywords
     - Domain check results
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

6. **datas.py**: Domain extraction and analysis
   - Loads spam emails from directory specified in SPAM_DATASET_DIR
   - Extracts sender domains from spam emails
   - Creates `unique_from_emails` set of known spam domains
   - Uses pandas and numpy for data processing
   - Configurable via environment variables

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
  - `SPAM_DATASET_DIR`: Directory containing spam emails for domain extraction

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
The detector.py file includes a main block that can test email files directly:
- Edit line 102 in detector.py to specify the file path to test
- Supports both .txt and .eml file formats
- Run with: `python detector.py`
- Current default test file: spam/spam_1.txt

## Environment Configuration

The project uses environment variables for configuration. Copy `.env.example` to `.env` and update as needed:

```bash
SPAM_WORDS_PATH=words/spam_words.txt
OUTPUT_FOLDER=words
SPAM_SOURCE_URL=https://www.activecampaign.com/blog/spam-words
TEMPLATE_FOLDER=website
SPAM_DATASET_DIR=spam
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
- **pandas**: Data manipulation for domain analysis (required by datas.py)
- **numpy**: Numerical operations (required by datas.py)

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

## Current Features Status

Working features:
- ✅ detector.py uses environment variables from .env file
- ✅ spamwords.py scrapes keywords and saves to words/spam_words.txt
- ✅ website.py Flask application serves on http://127.0.0.1:5000
- ✅ Environment configuration via .env file is functional
- ✅ Sample data files exist in ham/ and spam/ directories
- ✅ detector.py can test files directly (modify filepath on line 121)
- ✅ Domain checking with domaincheck() function
- ✅ Email report sending functionality in website.py
- ✅ datas.py loads spam domains from SPAM_DATASET_DIR

## Dependencies Note

Make sure to install pandas and numpy if not already installed:
```bash
pip install pandas numpy
```