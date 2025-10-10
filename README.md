# Phishing Email Detection System

A comprehensive Python-based phishing email detection application developed for the INF1002 Programming Fundamentals course at SIT. This system analyzes email content using multi-layered detection algorithms including keyword analysis, domain verification, and URL risk assessment to identify potential phishing threats.

## Team Members

- Ho Winthrop (2500940)
- Ho Shang Jay (2500526)
- Mohamed Raihan Bin Ismail (2503274)
- Matthew Dyason (2500503)
- Leticia Linus Jeraled (2501114)

**Team:** LAB-P5-7
**Course:** INF1002 Programming Fundamentals

---

## Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Detection Algorithm](#detection-algorithm)
- [API Endpoints](#api-endpoints)
- [Dependencies](#dependencies)
- [Testing](#testing)
- [License](#license)

---

## Features

### Core Detection Capabilities

- **Multi-Component Analysis System**
  - Keyword-based detection with position-weighted scoring
  - Domain verification with typosquatting detection using Levenshtein distance
  - Comprehensive URL risk assessment with WHOIS integration

- **File Format Support**
  - Accepts `.txt` plain text email files
  - Accepts `.eml` structured email files
  - HTML accept attribute for file type filtering

- **Risk Scoring System**
  - 5-tier risk assessment: VERY HIGH, HIGH, MEDIUM, LOW, VERY LOW
  - Component-level score capping to prevent false positives
  - Configurable thresholds via environment variables

- **Web Interface**
  - User-friendly Flask-based web application
  - Real-time email analysis with instant results
  - Optional email reporting for analysis results
  - Responsive Bootstrap design with modern UI/UX

- **Admin Dashboard**
  - Protected admin panel with authentication
  - Real-time analytics and statistics
  - Visual data representation with charts
  - Email classification distribution tracking
  - Top suspicious keywords frequency analysis

- **Data Persistence**
  - Automatic storage of analysis results
  - Timestamped email data archives
  - Historical analysis tracking

### Advanced Features

- **Intelligent Keyword Detection**
  - Position-based scoring (subject: 3 points, early body: 2 points, remaining body: 1 point)
  - CSV keyword consolidation and lemmatization
  - Regex word boundary matching for accurate detection

- **Domain Analysis**
  - Safe domain whitelist validation
  - Typosquatting detection using Levenshtein distance algorithm
  - Configurable similarity threshold

- **URL Risk Assessment**
  - Domain age verification (flags domains < 30 days old)
  - WHOIS data analysis with retry mechanism
  - IP address detection in URLs
  - HTTPS/HTTP protocol verification
  - URL length and subdirectory count analysis
  - Special character detection (@ symbol obfuscation)
  - Domain resolution validation

---

## System Architecture

### Backend Components

#### 1. **website.py** - Flask Web Application
The main application server that orchestrates all detection components.

**Key Functions:**
- `upload_file()`: Handles email file uploads and analysis
- `admin_login_json()`: Processes admin authentication
- `admin_page()`: Serves admin dashboard
- `parse_stored_emails()`: Extracts statistics from archived data
- `dashboard_data()`: Provides API endpoint for dashboard analytics

**Features:**
- Multi-component integration (keywords, domain, URL analysis)
- Component-level score capping (domain: 15, URL: 6, keywords: 15)
- Enhanced risk messaging for safe domains with suspicious content
- Session management for admin authentication
- Email reporting functionality

#### 2. **email_manage.py** - Email Parsing Engine
Extracts components from email files in multiple formats.

**Key Functions:**
- `parse_email_file(email_content)`: Parses .eml and plain text formats

**Capabilities:**
- Handles multipart MIME messages
- Extracts title, subject, and body
- UTF-8 decoding with error handling
- Supports structured and unstructured email formats

#### 3. **suspiciouswords.py** - Keyword Detection System
Analyzes email content for suspicious keywords with position-based scoring.

**Key Functions:**
- `consolidate_csv_keywords()`: Merges keyword sources into unified dataset
- `load_keywords(filepath)`: Loads keywords from CSV files
- `detection_subject(subject)`: Analyzes email subject (3 points per keyword)
- `detection_body(body)`: Analyzes email body with early/late detection
- `classify_email(subject, body)`: Returns keywords and suspicion score

**Features:**
- CSV-based keyword management
- Position-aware scoring (subject > early body > remaining body)
- Regex word boundary matching
- Environment-configurable scoring weights

#### 4. **domainchecker.py** - Domain Verification System
Validates sender domains and detects typosquatting attempts.

**Key Functions:**
- `distance_check(domain1, domain2)`: Calculates Levenshtein distance
- `email_titlecheck(email_title)`: Robust email extraction from title with fallback logic
- `domaincheck(email_title, safe_domains, threshold)`: Performs domain analysis

**Features:**
- Safe domain whitelist verification
- Typosquatting detection with configurable threshold (default: 4)
- Similarity scoring for suspicious domains
- Integration with safe domain database
- Improved email extraction handling (supports bracketed and non-bracketed formats)

#### 5. **suspiciousurl.py** - URL Risk Assessment Engine
Performs comprehensive URL analysis using multiple risk factors.

**Key Functions:**
- `extract_urls(email_body)`: Extracts all URLs from email content
- `assessing_risk_scores(email_body)`: Analyzes URLs and returns risk data

**Risk Factors:**
- Domain age analysis (< 30 days: HIGH, 30-120 days: MEDIUM, 120-365 days: LOW)
- WHOIS data verification with retry mechanism
- IP address detection in URLs
- HTTPS/HTTP protocol checking
- URL length analysis (> 75 characters flagged)
- Subdirectory count (> 3 flagged)
- '@' symbol detection for obfuscation

#### 6. **datas.py** - Domain Database Management
Extracts and maintains safe domain database from ham email dataset.

**Key Functions:**
- `load_data(directory, label)`: Loads emails from directory
- `list_of_domains(text)`: Extracts email domains from text

**Outputs:**
- `unique_from_emails`: Set of safe domains for validation

#### 7. **userdatastore.py** - Data Persistence Layer
Stores email analysis results for historical tracking and admin dashboard.

**Key Functions:**
- `storeDatainTxt(classification, keywords, total_score, EmailDomainMsg, email_text, url_reason_pairs, number_of_urls)`: Saves analysis to file

**Features:**
- Timestamped file naming
- Structured data format
- Error handling and status reporting

#### 8. **keyword_scrape_web.py** - Web Keyword Scraper
Scrapes spam keywords from external sources to update detection database.

**Key Functions:**
- `get_spam_words()`: Scrapes keywords from configured URL
- `save_csv(words, filename)`: Saves keywords to CSV

**Source:** Configurable via `SPAM_SOURCE_URL` environment variable

#### 9. **keyword_scrape_file.py** - File-Based Keyword Analyzer
Analyzes spam email datasets to extract frequent keywords.

**Key Functions:**
- `extract_email_content(file_path)`: Extracts subject and body from emails
- `clean_text(text)`: Normalizes and cleans text
- `get_words(text)`: Extracts meaningful words, filtering stop words
- `analyze_spam_directory(directory_path)`: Processes entire directories

**Features:**
- Top 2 words per file extraction
- Stop word filtering
- HTML tag and artifact removal
- Timestamp-based versioning

#### 10. **detectfunction.py** - Legacy Detection Module
Original phishing detection implementation (replaced by modular components).

### Frontend Components

#### 1. **website/index.html** - Main User Interface
Bootstrap-based responsive landing page for email analysis.

**Sections:**
- File upload area with drag-and-drop support
- Email content preview
- Analysis results display
- Risk metrics visualization
- URL analysis details
- Keyword detection results

**Features:**
- File type validation (accept=".eml,.txt,text/plain")
- Real-time file preview
- Color-coded risk levels
- Responsive design for mobile/tablet

#### 2. **website/adminPage.html** - Admin Dashboard
Protected analytics dashboard for monitoring system performance.

**Sections:**
- Safe vs. Phishing email statistics
- Pie chart for email distribution
- Bar chart for top 5 suspicious keywords
- Real-time data updates (30-second intervals)

**Features:**
- Chart.js integration for data visualization
- Auto-refresh functionality
- Session-based authentication

#### 3. **website/css/styles.css** - Main Stylesheet
Modern gradient-based design system for user interface.

**Design Features:**
- CSS custom properties for theming
- Gradient backgrounds
- Card-based layouts
- Smooth animations and transitions
- Responsive breakpoints

#### 4. **website/css/styles2.css** - Admin Dashboard Stylesheet
Specialized styling for admin analytics interface.

**Design Features:**
- Stat card designs
- Chart containers
- Dashboard grid layouts

#### 5. **website/js/script.js** - Frontend JavaScript
Handles file preview, admin authentication, and dashboard updates.

**Key Functions:**
- `previewFile()`: Displays uploaded file content
- `adminLoginPrompt()`: Handles admin login flow
- `fetchDashboardData()`: Retrieves analytics data
- `updateDashboard(data)`: Updates charts and statistics
- `initializePieChart()`: Creates email distribution chart
- `initializeBarChart()`: Creates keyword frequency chart

---

## Project Structure

```
INF1002-P5-7-Project/
│
├── website.py                    # Main Flask application
├── email_manage.py               # Email parsing engine
├── suspiciouswords.py            # Keyword detection system
├── domainchecker.py              # Domain verification module
├── suspiciousurl.py              # URL risk assessment engine
├── datas.py                      # Domain database management
├── userdatastore.py              # Data persistence layer
├── keyword_scrape_web.py         # Web keyword scraper
├── keyword_scrape_file.py        # File-based keyword analyzer
├── detectfunction.py             # Legacy detection module
│
├── website/                      # Frontend files
│   ├── index.html                # Main user interface
│   ├── adminPage.html            # Admin dashboard
│   ├── css/
│   │   ├── styles.css            # Main stylesheet
│   │   └── styles2.css           # Admin stylesheet
│   └── js/
│       └── script.js             # Frontend JavaScript
│
├── dataset/                      # Email datasets
│   ├── testing/                  # Test email files
│   │   ├── spam/                 # Spam email samples (12 files)
│   │   └── ham/                  # Legitimate email samples (12 files)
│   ├── kaggle/                   # Large datasets
│   │   ├── spam_2/               # Spam dataset for analysis
│   │   └── ham/                  # Ham dataset for safe domain extraction
│   └── safe_keep/                # Stored analysis results (timestamped)
│
├── keywords/                     # Keyword databases
│   ├── consolidate_keywords.csv  # Unified keyword list
│   ├── lemmatized_keywords.csv   # Processed keywords
│   ├── raw_data/                 # Source keyword files
│   │   ├── spam_words.csv
│   │   └── phishing_keywords.csv
│   └── lemmatizer.py             # Keyword processing scripts
│
├── .env.example                  # Environment configuration template
├── .env                          # Active environment config (not in repo)
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── CLAUDE.md                     # Claude Code assistant instructions
├── CODE_ANALYSIS_REPORT.md       # Security and code quality analysis
├── CURRENT_ISSUES.md             # Known issues and limitations
└── SYSTEM_DESIGN.md              # Detailed system architecture
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Step-by-Step Installation

1. **Clone the Repository**
```bash
git clone https://github.com/winthrop1/INF1002-P5-7-Project.git
cd INF1002-P5-7-Project
```

2. **Create Virtual Environment** (Recommended)
```bash
python3 -m venv .venv
```

3. **Activate Virtual Environment**
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure Environment Variables**
```bash
cp .env.example .env
```
Edit `.env` file with your configuration (see [Configuration](#configuration) section)

6. **Download NLTK Data** (if using lemmatization features)
```python
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
```

---

## Configuration

### Environment Variables

The system uses a `.env` file for configuration. Copy `.env.example` to `.env` and customize:

#### Flask Configuration
```env
TEMPLATE_FOLDER=website
SECRET_KEY=your-secret-key-here
```

#### Admin Credentials
```env
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
```

#### Dataset Paths
```env
HAM_DATASET_DIR=dataset/kaggle/ham
SPAM_DATASET_DIR=dataset/kaggle/spam_2
```

#### Email Reporting (Optional)
```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_KEY=your-app-specific-password
```

#### Keyword Configuration
```env
KEYWORDS_FOLDER=keywords
KEYWORDS_CONSOLIDATE_FILE=keywords/lemmatized_keywords.csv
KEYWORDS_RAW_FOLDER=keywords/raw_data
```

#### Scoring Weights

**Domain Analysis:**
```env
DOMAIN_SUSPICION_SCORE=2        # Score for unrecognized domain
DOMAIN_SIMILARITY_THRESHOLD=4   # Levenshtein distance threshold
```

**URL Analysis:**
```env
HIGH_DOMAIN_SCORE=3              # Domain < 30 days old
MEDIUM_DOMAIN_SCORE=2            # Domain 30-120 days old
LOW_DOMAIN_SCORE=1               # Domain 120-365 days old
HIGH_DOMAIN_EXPIRY_SCORE=2       # Expiring within 6 months
LOW_DOMAIN_EXPIRY_SCORE=1        # Expiring within 1 year
DOMAIN_UPDATE_SCORE=1            # Recently updated domain
IP_ADDRESS_SCORE=2               # IP address in URL
NO_HTTPS_SCORE=2                 # No HTTPS
HTTP_SCORE=1                     # HTTP instead of HTTPS
LONG_URL_SCORE=1                 # URL > 75 characters
AT_SYMBOL_SCORE=2                # '@' symbol in URL
SUBDIR_COUNT_SCORE=1             # > 3 subdirectories
UNRESOLVED_DOMAIN_SCORE=3        # Domain doesn't resolve
```

**Keyword Analysis:**
```env
SUBJECT_KEYWORD_SCORE=3          # Keyword in subject
EARLY_BODY_WORD_COUNT=100        # First N words = "early body"
EARLY_BODY_KEYWORD_SCORE=2       # Keyword in early body
BODY_KEYWORD_SCORE=1             # Keyword in remaining body
```

**Risk Thresholds:**
```env
MAX_DOMAIN_SCORE=15              # Cap for domain score
MAX_URL_SCORE=6                  # Cap for URL score
MAX_KEYWORD_SCORE=15             # Cap for keyword score

VERY_HIGH_RISK_THRESHOLD=16      # ≥16 points
HIGH_RISK_THRESHOLD=12           # 12-15 points
MEDIUM_RISK_THRESHOLD=8          # 8-11 points
LOW_RISK_THRESHOLD=4             # 4-7 points

PHISHING_SCORE=8                 # Threshold to classify as phishing
```

#### Web Scraping Configuration
```env
SPAM_SOURCE_URL=https://www.activecampaign.com/blog/spam-words
SPAM_WORDS_PATH=keywords/spam_words.txt
```

---

## Usage

### Running the Web Application

1. **Start the Flask Server**
```bash
python website.py
```

2. **Access the Application**
   - Open browser to: `http://127.0.0.1:5000`
   - Application runs in debug mode for development

3. **Analyze an Email**
   - Click "Choose file" or drag email file to upload area
   - Supported formats: `.txt`, `.eml`
   - Email content preview loads automatically
   - (Optional) Enter your email address to receive analysis report
   - Click "Analyze Email" button
   - View comprehensive results including:
     - Risk level classification
     - Total risk score
     - Domain verification results
     - URL analysis with reasons
     - Detected suspicious keywords

### Accessing Admin Dashboard

1. **Login to Admin Panel**
   - Click "Admin" in navigation bar
   - Enter admin credentials (from `.env` file)
   - Click OK to authenticate

2. **View Analytics**
   - Safe vs. Phishing email counts
   - Email distribution pie chart
   - Top 5 suspicious keywords bar chart
   - Auto-refreshes every 30 seconds

3. **Logout**
   - Click "Logout" in navigation bar

### Command-Line Tools

#### Update Keyword Database from Web
```bash
python keyword_scrape_web.py
```
Scrapes latest spam keywords from configured URL

#### Consolidate Keywords
```bash
python suspiciouswords.py
```
Merges all CSV keyword sources into single file

#### Test Email Parsing
```bash
python email_manage.py
```
Tests email parsing functionality on test file

#### Extract Safe Domains
```bash
python datas.py
```
Builds safe domain database from ham emails

---

## Detection Algorithm

### Multi-Component Risk Scoring

The system uses a sophisticated multi-layered approach:

#### 1. Keyword Detection (`suspiciouswords.py`)

```python
# Position-based scoring
if keyword in subject:
    score += SUBJECT_KEYWORD_SCORE  # Default: 3

elif keyword in first_100_words_of_body:
    score += EARLY_BODY_KEYWORD_SCORE  # Default: 2

elif keyword in remaining_body:
    score += BODY_KEYWORD_SCORE  # Default: 1
```

**Keyword Detection Features:**
- Regex word boundary matching (`\b` anchors)
- Case-insensitive matching
- CSV-based keyword database
- Position-aware scoring (subject > early > late)

#### 2. Domain Analysis (`domainchecker.py`)

```python
# Extract email from title (handles <email> and plain text)
email = email_titlecheck(email_title)
domain = "@" + email.split('@')[1]

# Typosquatting detection
domain_distance = levenshtein_distance(sender_domain, safe_domain)

if domain not in safe_domains:
    score += DOMAIN_SUSPICION_SCORE  # Default: 2

if domain_distance <= THRESHOLD:  # Default threshold: 4
    score += domain_distance
    # Example: "microsft.com" vs "microsoft.com" = 1 change
```

**Domain Analysis Features:**
- Levenshtein distance algorithm
- Safe domain whitelist
- Similarity threshold configuration
- Typosquatting alerts

#### 3. URL Risk Assessment (`suspiciousurl.py`)

```python
# Multi-factor URL analysis
if domain_age < 30_days:
    score += HIGH_DOMAIN_SCORE  # Default: 3

if ip_address_in_url:
    score += IP_ADDRESS_SCORE  # Default: 2

if not uses_https:
    score += NO_HTTPS_SCORE  # Default: 2

if url_length > 75:
    score += LONG_URL_SCORE  # Default: 1

if '@' in url:
    score += AT_SYMBOL_SCORE  # Default: 2

if subdirectory_count > 3:
    score += SUBDIR_COUNT_SCORE  # Default: 1
```

**URL Analysis Features:**
- WHOIS data integration
- Domain age verification
- Protocol analysis (HTTPS/HTTP)
- Structural analysis (length, subdirectories)
- Obfuscation detection (@ symbol, IP addresses)

#### 4. Final Risk Calculation (`website.py`)

```python
# Component-level capping
domain_capped = min(domain_score, MAX_DOMAIN_SCORE)  # Cap: 15
url_capped = min(url_score, MAX_URL_SCORE)  # Cap: 6
keywords_capped = min(keywords_score, MAX_KEYWORD_SCORE)  # Cap: 15

total_risk_score = domain_capped + url_capped + keywords_capped

# Risk level assignment
if total_risk_score >= 16:
    risk_level = "VERY HIGH"
elif total_risk_score >= 12:
    risk_level = "HIGH"
elif total_risk_score >= 8:
    risk_level = "MEDIUM"
elif total_risk_score >= 4:
    risk_level = "LOW"
else:
    risk_level = "VERY LOW"
```

**Final Classification:**
```python
# Uses configurable PHISHING_SCORE threshold (default: 8)
classification = "Safe" if total_risk_score <= PHISHING_SCORE else "Phishing"
```

### Algorithm Flow

```
Email Upload
    ↓
Parse Email (email_manage.py)
    ↓
Extract: Title, Subject, Body
    ↓
┌─────────────────┬──────────────────┬─────────────────┐
│                 │                  │                 │
│ Keyword         │ Domain           │ URL             │
│ Detection       │ Verification     │ Analysis        │
│                 │                  │                 │
│ suspiciouswords │ domainchecker    │ suspiciousurl   │
│                 │                  │                 │
│ Score: 0-15     │ Score: 0-15      │ Score: 0-6      │
└─────────────────┴──────────────────┴─────────────────┘
    │                 │                  │
    └─────────────────┴──────────────────┘
                      ↓
            Apply Score Caps
                      ↓
            Sum Total Score
                      ↓
         Assign Risk Level
                      ↓
    Classify (Safe/Phishing)
                      ↓
          Display Results
```

---

## API Endpoints

### User Endpoints

#### `GET /` - Main Application Page
Returns the main email analysis interface.

#### `POST /` - Analyze Email
**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - `emailfile`: File upload (.txt or .eml)
  - `userEmail`: (Optional) User email for report

**Response:**
- HTML page with analysis results
- Risk level, score, keywords, URL analysis, domain check

### Admin Endpoints

#### `POST /admin-login-json` - Admin Authentication
**Request:**
```json
{
  "username": "admin_username",
  "password": "admin_password"
}
```

**Response:**
```json
{
  "success": true
}
```
or
```json
{
  "success": false,
  "error": "Invalid email or password."
}
```

#### `GET /admin` - Admin Dashboard
Returns admin dashboard page (requires authentication).

#### `GET /api/dashboard-data` - Dashboard Analytics
**Response:**
```json
{
  "safe_count": 42,
  "phishing_count": 18,
  "total_emails": 60,
  "top_keywords": [
    {"keyword": "urgent", "count": 15},
    {"keyword": "verify", "count": 12},
    {"keyword": "account", "count": 10},
    {"keyword": "suspended", "count": 8},
    {"keyword": "click", "count": 7}
  ]
}
```

#### `GET /logout` - Logout
Clears admin session and redirects to home page.

---

## Dependencies

### Core Python Packages

```txt
flask==3.1.2               # Web framework
requests==2.32.5           # HTTP library for web scraping
lxml==6.0.1                # HTML/XML processing
python-dotenv==1.1.1       # Environment variable management
pandas>=1.5.0              # Data manipulation
validators                 # URL/domain validation
whois                      # Domain WHOIS lookup
nltk                       # Natural language processing
```

### Frontend Libraries

- **Bootstrap 5.3.0** - Responsive CSS framework
- **Font Awesome 6.3.0** - Icon library
- **Chart.js 2.8.0** - Data visualization for admin dashboard

### Standard Library Modules

- `re` - Regular expressions
- `os` - File system operations
- `csv` - CSV file handling
- `glob` - File pattern matching
- `smtplib` - Email sending
- `email` - Email parsing
- `datetime` - Timestamp generation
- `collections` - Counter for frequency analysis

### Installation

```bash
pip install -r requirements.txt
```

---

## Testing

### Test Email Datasets

Located in `dataset/testing/`:

**Spam Emails:**
- `spam/spam_1.txt` through `spam/spam_12.txt`
- Known phishing emails for detection accuracy testing

**Ham Emails:**
- `ham/ham_1.txt` through `ham/ham_12.txt`
- Legitimate emails for false positive testing

### Manual Testing

#### Test Email Parsing
```bash
python email_manage.py
```
Tests email parsing on configured test file.

#### Test Individual Components
```python
from email_manage import parse_email_file
from suspiciouswords import classify_email
from domainchecker import domaincheck
from suspiciousurl import assessing_risk_scores

# Load test email
with open('dataset/testing/spam/spam_1.txt', 'r') as f:
    email_content = f.read()

# Parse email
title, subject, body = parse_email_file(email_content)

# Run detection components
keywords, keywords_score = classify_email(subject, body)
domain_msg, distance_msg, domain_score = domaincheck(title)
reasons, url_score, url_pairs, num_urls, num_domains = assessing_risk_scores(body)

# Calculate total
total_score = keywords_score + domain_score + url_score
print(f"Total Risk Score: {total_score}")
```

### Web Interface Testing

1. Start the application: `python website.py`
2. Navigate to `http://127.0.0.1:5000`
3. Upload test files from `dataset/testing/`
4. Verify risk scores and classifications
5. Test admin dashboard functionality
6. Verify data storage in `dataset/safe_keep/`


