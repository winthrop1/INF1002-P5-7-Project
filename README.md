# INF1002-P5-7 Phishing Email Detection System

## Group Members:
- Ho Winthrop 2500940
- Ho Shang Jay 2500526
- Mohamed Raihan Bin Ismail 2503274
- Matthew Dyason 2500503
- Leticia Linus Jeraled 2501114

## 📧 Project Overview

A Python-based phishing email detection system developed for the INF1002 Programming Fundamentals course. This application analyzes email content to detect potential phishing attempts using keyword-based scoring algorithms and domain verification.`

## 🎯 Features

- **Email Analysis**: Processes both `.txt` and `.eml` email files
- **Multi-Component Detection**:
  - **Keyword Detection**: Position-based scoring (subject/early body/remaining body)
  - **Domain Analysis**: Levenshtein distance for typosquatting detection
  - **URL Analysis**: Comprehensive URL risk assessment with WHOIS data
- **Integrated Risk Scoring**: 5-tier assessment (VERY HIGH/HIGH/MEDIUM/LOW/VERY LOW)
- **Web Interface**: User-friendly Flask web application for email upload and analysis
- **Email Reports**: Optional email reporting with detailed analysis results
- **Enhanced Messaging**: Alerts users when safe domains have suspicious content
- **Environment Configuration**: Fully configurable via .env file

## 🏗️ System Architecture

### Core Components

#### 1. **suspiciouswords.py** - Enhanced Keyword Detection
- Loads consolidated keywords from CSV files
- Weighted scoring system:
  - Subject keywords: 3 points (configurable via SUBJECT_KEYWORD_SCORE)
  - Early body keywords (first 100 words): 2 points
  - Remaining body keywords: 1 point
- Uses regex word boundary matching for accuracy
- Returns: (classification, keywords, suspicion_score)

#### 2. **domainchecker.py** - Domain Analysis & Typosquatting Detection
- Implements Levenshtein distance algorithm
- Checks sender domains against known safe domains
- Detects typosquatting attempts (configurable threshold: 4)
- Simplified email domain parsing logic
- Distinguishes between safe and unrecognized domains
- Returns: (domain_message, suspicion_score)

#### 3. **suspiciousurl.py** - Comprehensive URL Analysis
- Multi-factor URL risk assessment:
  - Domain resolution check before analysis
  - Domain age analysis (<30 days flagged)
  - WHOIS data with retry mechanism (max 3 retries)
  - IP address detection in URLs
  - HTTPS/HTTP protocol checking
  - URL length analysis (>75 characters flagged)
  - Subdirectory count (>3 flagged)
  - '@' symbol detection for URL obfuscation
- Handles emails with no URLs gracefully
- Returns: (reasons_list, url_suspicion_score)

#### 4. **website.py** - Integrated Flask Web Application
- Multi-component analysis integration
- Combines scores from keywords, domain, and URL analysis
- 5-tier risk scoring:
  - VERY HIGH: ≥9 points
  - HIGH: 7-8 points
  - MEDIUM: 5-6 points
  - LOW: 3-4 points
  - VERY LOW: <3 points
- Enhanced risk messaging for safe domains with suspicious content
- Optional user email input for receiving reports
- Runs on http://127.0.0.1:5000 in debug mode

#### 5. **email_manage.py** - Email Parsing
- Handles both .eml structured emails and plain text
- Extracts: title, subject, body
- Supports multipart MIME message parsing
- Error handling for malformed content

#### 6. **datas.py** - Domain Extraction
- Loads spam emails from SPAM_DATASET_DIR
- Extracts sender domains from spam dataset
- Creates `unique_from_emails` set
- Uses pandas for data processing

### Frontend Components

- **website/index.html**: Bootstrap-based responsive UI
- **website/style.css**: Custom styling for the interface

## 📁 Project Structure

```
INF1002-P5-7-Project/
│
├── detectfunction.py          # Main phishing detection logic
├── website.py                 # Flask web application server
├── spamwords.py              # Spam keyword scraper
├── datas.py                  # Domain extraction and analysis
│
├── website/                   # Web interface templates
│   ├── index.html            # Main HTML template
│   └── style.css             # Custom CSS styles
│
├── words/                     # Keyword database
│   └── spam_words.txt        # Master list of spam keywords
│
├── spam/                      # Sample phishing emails for testing
│   ├── spam_1.txt
│   ├── spam_2.txt
│   └── ... (12 files total)
│
├── ham/                       # Sample legitimate emails for testing
│   ├── ham_1.txt
│   ├── ham_2.txt
│   └── ... (12 files total)
│
├── dataset/                   # Large email dataset
│   ├── hamEmails/            # Legitimate email samples
│   └── spamEmails/           # Spam email samples
│
├── requirements.txt           # Python dependencies
├── .env.example              # Environment configuration template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/winthrop1/INF1002-P5-7-Project.git
cd INF1002-P5-7-Project
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

### Environment Configuration

Create a `.env` file with the following variables:
```env
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

## 💻 Usage

### Running the Web Application

```bash
python website.py
```
Access the application at: http://127.0.0.1:5000

### Testing Detection System

```bash
python detectfunction.py
```
This will test the detection system with sample spam and ham files.

### Updating Spam Keywords

```bash
python spamwords.py
```
This will scrape and update the spam keywords database.

### Extracting Domain Data

```bash
python datas.py
```
This will analyze the dataset and extract spam domains.

## 🔍 How It Works

1. **Upload Email**: User uploads an email file (.txt or .eml format)
2. **Parse Content**: System extracts title, subject, and body using `email_manage`
3. **Multi-Component Analysis**:
   - **Keyword Detection** (`suspiciouswords.py`):
     - Subject keywords: 3 points each
     - Early body keywords (first 100 words): 2 points each
     - Remaining body keywords: 1 point each
   - **Domain Analysis** (`domainchecker.py`):
     - Levenshtein distance check against safe domains
     - Typosquatting detection with threshold
     - Unrecognized domain scoring
   - **URL Analysis** (`suspiciousurl.py`):
     - Domain resolution and WHOIS lookup
     - Domain age, expiration, and update analysis
     - IP address, HTTPS, URL length, and special character checks
4. **Risk Scoring**:
   - Combines all component scores
   - 5-tier assessment: VERY HIGH (≥9), HIGH (7-8), MEDIUM (5-6), LOW (3-4), VERY LOW (<3)
5. **Enhanced Messaging**:
   - Alerts if safe domains have suspicious content
   - Provides detailed reasons for each suspicion factor
6. **Display Results**: Shows classification, risk level, score, keywords, and URL properties
7. **Email Report** (Optional): Sends detailed analysis to user's email

## 📊 Detection Algorithm

The detection system uses a multi-component scoring algorithm:

```python
# 1. Keyword Scoring (suspiciouswords.py)
if keyword_in_subject:
    keywords_score += SUBJECT_KEYWORD_SCORE  # Default: 3
elif keyword_in_early_body (first 100 words):
    keywords_score += EARLY_BODY_KEYWORD_SCORE  # Default: 2
elif keyword_in_remaining_body:
    keywords_score += BODY_KEYWORD_SCORE  # Default: 1

# 2. Domain Scoring (domainchecker.py)
if domain_not_in_safe_list:
    domain_score += SENDER_KEYWORD_SCORE  # Default: 2
if similar_to_safe_domain (Levenshtein distance ≤ threshold):
    domain_score += distance_value

# 3. URL Scoring (suspiciousurl.py)
if domain_age < 30_days:
    url_score += HIGH_DOMAIN_SCORE  # Default: 3
if domain_has_ip_address:
    url_score += IP_ADDRESS_SCORE  # Default: 2
if no_https:
    url_score += NO_HTTPS_SCORE  # Default: 2
# ... additional URL checks

# 4. Total Risk Assessment
total_risk_score = keywords_score + domain_score + url_score

if total_risk_score >= 9:
    risk_level = "VERY HIGH"
elif total_risk_score >= 7:
    risk_level = "HIGH"
elif total_risk_score >= 5:
    risk_level = "MEDIUM"
elif total_risk_score >= 3:
    risk_level = "LOW"
else:
    risk_level = "VERY LOW"
```

## 🧪 Testing

The project includes sample email files for testing:

- **Spam samples**: Located in `spam/` directory (12 files)
- **Ham samples**: Located in `ham/` directory (12 files)
- **Large dataset**: Available in `dataset/` directory

Run the detection test:
```bash
python detectfunction.py
```

## 📦 Dependencies

- **flask==3.1.2**: Web framework for the application
- **requests==2.32.5**: HTTP library for web scraping
- **lxml==6.0.1**: XML/HTML processing
- **python-dotenv==1.1.1**: Environment variable management
- **pandas>=1.5.0**: Data manipulation for domain analysis
- **validators**: URL and domain validation
- **whois**: Domain registration information lookup
- **nltk**: Natural Language Processing (NLP) for data manipulation and cleaning

Install all dependencies:
```bash
pip install -r requirements.txt
```

## 👥 Team P5-7

Developed by Team P5-7 for INF1002 Programming Fundamentals course.