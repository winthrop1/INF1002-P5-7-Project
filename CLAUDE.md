# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

INF1002-P5-7-Project: A phishing email detection system built with Python and Flask for the INF1002 Programming Fundamentals course. The application analyzes email content to detect potential phishing attempts using keyword-based scoring algorithms.

## Architecture

### Enhanced Detection System (NEW - Priority 1 Implementation Complete)

1. **enhanced_detector.py**: Main orchestrator for comprehensive phishing detection
   - Coordinates all detection components (RuleManager, PatternMatcher, ScoringEngine)
   - Parses emails and extracts components (subject, body, URLs, sender)
   - Performs multi-layered analysis with rule matching and pattern detection
   - Generates risk assessments with confidence scores and recommendations
   - Supports both .eml and plain text formats
   - Performance: <400ms average analysis time

2. **rules_manager.py**: Dynamic rule management system
   - Loads and caches JSON-based detection rules from `rules/` directory
   - Manages 187 categorized rules across 7 risk categories
   - Supports regex and keyword pattern matching
   - Implements rule validation and statistics tracking
   - Enables runtime rule addition and modification

3. **pattern_matcher.py**: Advanced pattern matching engine
   - Regex pattern compilation and caching for performance
   - Fuzzy matching for typo detection (threshold-based)
   - URL extraction and analysis (shorteners, IP addresses, suspicious TLDs)
   - Suspicious pattern detection (excessive caps, hidden text, unicode abuse)
   - Text entropy calculation for obfuscation detection
   - Context extraction for matched patterns

4. **scoring_engine.py**: Sophisticated risk scoring system
   - Multi-tier risk levels: CRITICAL (9-10), HIGH (7-8.9), MEDIUM (4-6.9), LOW (1-3.9), SAFE (0-0.9)
   - Category-based weight multipliers (Social Engineering: 2.0x, Urgency: 1.8x, etc.)
   - Confidence calculation based on rule diversity and match count
   - Generates actionable recommendations based on risk level
   - Detailed reporting with category breakdowns

5. **keyword_categorizer.py**: Automated keyword categorization tool
   - Processes existing spam_words.txt into categorized rules
   - Automatic classification into 7 categories based on pattern matching
   - Generates detection_rules.json with 187 categorized rules
   - Creates mapping files and detailed categorization reports

6. **detector_comparison.py**: Performance comparison tool
   - Compares original vs enhanced detector accuracy
   - Measures detection speed and false positive/negative rates
   - Generates detailed comparison reports
   - Saves results to comparison_results.json

7. **suspiciousurl.py**: URL analysis and verification system
   - Extracts URLs from email content using regex patterns
   - Analyzes domain reputation and registration information
   - Detects URL shorteners and suspicious TLDs
   - Checks for IP addresses in URLs instead of domains
   - Uses WHOIS lookup for domain analysis
   - Scores URLs based on multiple risk factors

8. **csv_processor.py**: CSV keyword processing and integration
   - Processes CSV keyword files (top_2_words_per_file.csv, top_2_words_spam.csv)
   - Categorizes keywords into 7 detection categories automatically
   - Integrates CSV data with existing JSON detection rules
   - Generates comprehensive keyword mappings and statistics

9. **word_frequency_analyzer.py**: Statistical text analysis
   - Extracts email content from files and analyzes word frequency
   - Focuses on subject and body content, skipping headers
   - Generates frequency statistics for spam/ham classification
   - Exports analysis results to CSV format for further processing

10. **main.py**: Integration orchestrator
    - Coordinates multiple detection components
    - Integrates URL analysis with keyword detection
    - Processes email files through the complete detection pipeline
    - Combines scores from different analysis methods

### Core Components (Current Implementation)

1. **suspiciouswords.py**: Enhanced keyword detection system
   - Loads consolidated keywords from CSV files via `consolidate_csv_keywords()`
   - Implements weighted scoring system:
     - Subject keywords: 3 points each (configurable via SUBJECT_KEYWORD_SCORE)
     - Early body keywords (first 100 words): 2 points each (EARLY_BODY_KEYWORD_SCORE)
     - Remaining body keywords: 1 point each (BODY_KEYWORD_SCORE)
   - Uses regex word boundary matching for accurate detection
   - Returns tuple: (classification, keywords, keywords_suspicion_score)
   - Environment-configurable thresholds and scoring weights

2. **domainchecker.py**: Domain analysis and typosquatting detection
   - Implements Levenshtein distance algorithm for similarity checking
   - Checks sender domains against known safe domains list
   - Detects typosquatting attempts with configurable threshold (default: 4)
   - Extracts email domain from title using simplified parsing logic
   - Environment-configurable scoring via SENDER_KEYWORD_SCORE
   - Improved messaging: distinguishes between safe domains and unrecognized domains
   - Returns tuple: (EmailDomainMsg, domain_suspicion_score)

3. **suspiciousurl.py**: Comprehensive URL analysis system
   - Extracts URLs from email content using regex patterns
   - Handles emails with no URLs gracefully (returns appropriate message)
   - Multi-factor URL risk assessment:
     - Domain resolution check before analysis
     - Domain age analysis (new domains <30 days flagged)
     - WHOIS data analysis with retry mechanism (max 3 retries)
     - IP address detection in URLs
     - HTTPS/HTTP protocol checking
     - URL length analysis (>75 characters flagged)
     - Subdirectory count analysis (>3 flagged)
     - '@' symbol detection for URL obfuscation
   - Risk scoring with tiered levels: VERY_LOW, LOW, MEDIUM, HIGH
   - Improved error handling for unresolved domains
   - Returns tuple: (reasons, url_suspicion_score)

4. **website.py**: Integrated Flask web application
   - Multi-component analysis integration
   - Combines scores from keywords, domain, and URL analysis
   - Comprehensive risk scoring:
     - VERY HIGH: ≥9 points
     - HIGH: 7-8 points
     - MEDIUM: 5-6 points
     - LOW: 3-4 points
     - VERY_LOW: <3 points
   - Enhanced risk messaging: Alerts users when safe domains have suspicious content
   - Email reporting functionality with detailed analysis results
   - Optional user email input for receiving analysis reports
   - Template folder: `website/`
   - Debug mode for development

5. **main.py**: Detection pipeline orchestrator
   - Coordinates email parsing via `email_manage.parse_email_file()`
   - Integrates keyword detection via `suspiciouswords.classify_email()`
   - Performs domain checking via `domainchecker.domaincheck()`
   - Executes URL analysis via `suspiciousurl.assessing_risk_scores()`
   - Combines all detection components for comprehensive analysis

6. **email_manage.py**: Email parsing and content extraction
   - Handles both .eml structured emails and plain text formats
   - Extracts email components: title, subject, body
   - Supports multipart MIME message parsing
   - Error handling for malformed email content
   - Returns tuple: (title, subject, body)

7. **datas.py**: Domain extraction and analysis
   - Loads spam emails from directory specified in SPAM_DATASET_DIR
   - Extracts sender domains from spam emails
   - Creates `unique_from_emails` set of known spam domains
   - Uses pandas and numpy for data processing
   - Configurable via environment variables

### Legacy Components

8. **keyword_scrape_web.py**: Web scraper for keyword database maintenance
   - Scrapes keywords from external sources
   - Updates keyword databases for detection system
   - Can be run independently to refresh keyword lists

9. **website/index.html**: Frontend user interface
   - Bootstrap-based responsive design
   - File upload form with validation
   - Results display with color coding and risk levels
   - Clean, user-friendly interface

10. **website/style.css**: Custom CSS styling
    - Additional styling on top of Bootstrap
    - Custom color schemes and layouts

### Rules and Configuration Structure (NEW)

- **rules/**: Detection rules and configuration
  - `detection_rules.json`: 187 categorized detection rules
  - `keyword_category_mapping.json`: Keyword to category mappings
  - `categorization_report.txt`: Detailed categorization report

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

#### Using Current Implementation (Recommended)
```python
from email_manage import parse_email_file
from suspiciouswords import classify_email
from domainchecker import domaincheck
from suspiciousurl import assessing_risk_scores

# Test with sample email content
email_content = """From: suspicious@new-domain.com
Subject: Urgent: Win $1000 now!
Click here for free money: http://suspicious-site.com/claim"""

# Parse email components
title, subject, body = parse_email_file(email_content)

# Run individual detection components
classification, keywords, keywords_score = classify_email(subject, body)
domain_msg, domain_score = domaincheck(title)
url_reasons, url_score = assessing_risk_scores(body)

# Calculate total risk
total_score = keywords_score + domain_score + url_score

print(f"Classification: {classification}")
print(f"Keyword Score: {keywords_score}")
print(f"Domain Score: {domain_score}")
print(f"URL Score: {url_score}")
print(f"Total Risk Score: {total_score}")
print(f"Keywords found: {keywords}")
print(f"Domain analysis: {domain_msg}")
print(f"URL analysis: {url_reasons}")
```

#### Using Main Pipeline
```python
from main import process_email_file

# Test with email file
email_file = "dataset/testing/spam_1.txt"
process_email_file(email_file)
```

### Comparing Detectors
```bash
python detector_comparison.py
```
This will test both detectors on all sample emails and generate a comparison report.

### Additional Analysis Tools

#### URL Analysis
```bash
python suspiciousurl.py
```
Analyzes URLs in emails for suspicious characteristics including domain reputation, URL shorteners, and phishing indicators.

#### CSV Data Processing
```bash
python csv_processor.py
```
Processes CSV keyword files and integrates them into JSON detection rules.

#### Word Frequency Analysis
```bash
python word_frequency_analyzer.py
```
Analyzes word frequency patterns in email datasets for keyword extraction.

#### Main Integration Script
```bash
python main.py
```
Integrates multiple detection components including URL analysis and keyword detection.

### Updating Spam Keywords Database

#### Scrape New Keywords
```bash
python spamwords.py
```
This will scrape the latest spam keywords and update `words/spam_words.txt`.

#### Categorize Keywords into Rules
```bash
python keyword_categorizer.py
```
This will categorize all keywords and generate `rules/detection_rules.json`.

### Testing with Sample Data

#### Run Complete Test Suite
```bash
python test_hybrid_terminal.py
```
This runs comprehensive tests comparing both detection systems on all sample files.

#### Quick Spam File Testing
```bash
python test_spam_files.py
```
Tests enhanced detector with files in the ham/ directory.

#### Manual Testing
The detectfunction.py file includes a main block that can test email files directly:
- Edit the file path in detectfunction.py to specify test file
- Supports both .txt and .eml file formats
- Run with: `python detectfunction.py`

## Environment Configuration

The project uses environment variables for configuration. Copy `.env.example` to `.env` and update as needed:

```bash
# Flask Configuration
TEMPLATE_FOLDER=website

# Dataset Configuration
HAM_DATASET_DIR=dataset/kaggle/ham
SPAM_DATASET_DIR=dataset/kaggle/spam_2

# Email Configuration (for sending reports)
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-email-password
EMAIL_KEY=your-app-password

# Keywords Configuration
KEYWORDS_FOLDER=keywords
KEYWORDS_CONSOLIDATE_FILE=keywords/consolidate_keywords.csv
KEYWORDS_RAW_FOLDER=keywords/raw_data

# Domain Analysis Configuration
SENDER_KEYWORD_SCORE=2
DISTANCE_THRESHOLD=0.8
DISTANCE_SCORE=2

# URL Analysis Configuration
HIGH_DOMAIN_SCORE=3
MEDIUM_DOMAIN_SCORE=2
LOW_DOMAIN_SCORE=1
LOW_DOMAIN_EXPIRY_SCORE=1
HIGH_DOMAIN_EXPIRY_SCORE=2
DOMAIN_UPDATE_SCORE=1
IP_ADDRESS_SCORE=2
NO_HTTPS_SCORE=2
HTTP_SCORE=1
LONG_URL_SCORE=1
AT_SYMBOL_SCORE=2
SUBDIR_COUNT_SCORE=1
UNRESOLVED_DOMAIN_SCORE=3

# Keyword Detection Configuration
SUBJECT_KEYWORD_SCORE=3
EARLY_BODY_WORD_COUNT=100
EARLY_BODY_KEYWORD_SCORE=2
BODY_KEYWORD_SCORE=1

# Maximum Score Limits
MAX_DOMAIN_SCORE=15
MAX_SENDER_SCORE=6
MAX_KEYWORD_SCORE=15

# Weight Configuration
SENDER_WEIGHT=1
DOMAIN_WEIGHT=2
KEYWORD_WEIGHT=2

# Spam Words Scraping Configuration
SPAM_SOURCE_URL=https://www.activecampaign.com/blog/spam-words
SPAM_WORDS_PATH=keywords/spam_words.txt
SPAM_SOURCE_PATH=dataset/kaggle/spam_2

# Testing Configuration
TEST_EMAIL_FILE=dataset/testing/spam/spam_1.txt
```

Note: The code now uses environment variables instead of hardcoded paths and scores, making it portable and configurable across different systems.

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
- **pandas>=1.5.0**: Data manipulation for domain analysis
- **validators**: URL and domain validation
- **whois**: Domain registration information lookup

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
- The scoring system can be tuned by adjusting weights in detectfunction.py

## Current Features Status

### Integrated Detection System (Current Implementation)
- ✅ Multi-component phishing detection system
- ✅ Keyword detection with position-based scoring (subject/early body/late body)
- ✅ Domain analysis with Levenshtein distance typosquatting detection
- ✅ Comprehensive URL analysis with WHOIS data, age, and reputation checking
- ✅ Integrated risk scoring across all components
- ✅ Multi-tier risk assessment (VERY HIGH/HIGH/MEDIUM/LOW/VERY_LOW)
- ✅ Environment-configurable scoring weights and thresholds
- ✅ Flask web application with integrated analysis pipeline
- ✅ Email reporting functionality with detailed analysis results
- ✅ Optional user email input for receiving reports
- ✅ Support for both .eml and plain text email formats
- ✅ Regex-based pattern matching with word boundary detection
- ✅ CSV keyword consolidation and processing
- ✅ Enhanced risk messaging for safe domains with suspicious content
- ✅ Improved error handling and graceful degradation
- ✅ No-URL email handling with appropriate messaging

### Core Components Status
- ✅ suspiciouswords.py: Enhanced keyword detection with CSV consolidation
- ✅ domainchecker.py: Domain analysis with similarity checking
- ✅ suspiciousurl.py: Multi-factor URL risk assessment
- ✅ email_manage.py: Robust email parsing for multiple formats
- ✅ main.py: Integration pipeline orchestrating all components
- ✅ website.py: Web interface with comprehensive result display
- ✅ datas.py: Domain extraction from spam dataset
- ✅ Environment configuration via .env file
- ✅ Sample data files in dataset/ directory structure

### Testing and Validation
- ✅ Individual component testing capabilities
- ✅ Integrated pipeline testing via main.py
- ✅ Web interface testing via website.py
- ✅ Environment-based configuration testing
- ✅ Multi-format email file support (.eml, .txt)

## Dependencies Note

Make sure to install pandas and numpy if not already installed:
```bash
pip install pandas numpy
```