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

### Core Components (Original)

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

#### Using Enhanced Detector (Recommended)
```python
from enhanced_detector import EnhancedPhishingDetector

# Initialize detector
detector = EnhancedPhishingDetector()

# Test with a sample email
email_text = "Subject: Win $1000 now!\nClick here for free money..."
assessment = detector.analyze_email(email_text)

# Display results
print(f"Classification: {assessment.classification}")
print(f"Risk Level: {assessment.risk_level}")
print(f"Score: {assessment.score}/10")
print(f"Confidence: {assessment.confidence*100:.0f}%")
print(f"Recommendations: {assessment.recommendations}")
```

#### Using Original Detector
```python
from detector import classify_email

# Test with a sample email (requires subject and body separately)
subject = "Win $1000 now!"
body = "Click here for free money..."
classification, keywords, score = classify_email(subject, body)
print(f"Classification: {classification}")
print(f"Score: {score}")
print(f"Keywords found: {keywords}")
```

### Comparing Detectors
```bash
python detector_comparison.py
```
This will test both detectors on all sample emails and generate a comparison report.

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

### Enhanced Detection System (NEW)
- ✅ Enhanced detector with 187 categorized rules
- ✅ Multi-tier risk assessment (CRITICAL/HIGH/MEDIUM/LOW/SAFE)
- ✅ Pattern matching with regex, fuzzy matching, and context extraction
- ✅ URL analysis for phishing indicators
- ✅ Confidence scoring and actionable recommendations
- ✅ Performance: <400ms analysis time
- ✅ Automated keyword categorization from spam_words.txt
- ✅ Detector comparison tool for performance analysis

### Original System (Maintained for Compatibility)
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