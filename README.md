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
- **Keyword Detection**: Identifies suspicious words in email subject and body
- **Domain Verification**: Checks sender domains against known spam domains
- **Web Interface**: User-friendly Flask web application for email upload and analysis
- **Email Reports**: Sends analysis results to users via email
- **Automated Keyword Updates**: Web scraper to maintain up-to-date spam keyword database

## 🏗️ System Architecture

### Core Components

#### 1. **detectfunction.py** - Main Detection Engine
- Loads spam keywords from `words/spam_words.txt`
- Implements weighted scoring system:
  - Subject keywords: 3 points each
  - Body keywords: 1 point each
- Classification: Score > 0 = Phishing, Score = 0 = Safe
- Parses email content (supports both plain text and .eml formats)
- Performs domain checking against known spam domains

#### 2. **website.py** - Flask Web Application
- Provides file upload interface for email analysis
- Displays classification results with risk scores
- Sends email reports to users with analysis details
- Runs on http://127.0.0.1:5000 in debug mode

#### 3. **spamwords.py** - Keyword Database Updater
- Scrapes spam keywords from activecampaign.com
- Filters phrases to maximum 5 words for better matching
- Automatically saves to `words/spam_words.txt`

#### 4. **datas.py** - Domain Analysis
- Extracts sender domains from spam email dataset
- Creates set of known spam domains for verification
- Processes emails from dataset directory

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
SPAM_WORDS_PATH=words/spam_words.txt
OUTPUT_FOLDER=words
SPAM_SOURCE_URL=https://www.activecampaign.com/blog/spam-words
TEMPLATE_FOLDER=website
SPAM_DATASET_DIR=spam
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
2. **Parse Content**: System extracts subject, body, and sender information
3. **Keyword Analysis**:
   - Scans for suspicious keywords in subject (3 points each)
   - Scans for suspicious keywords in body (1 point each)
4. **Domain Check**: Verifies if sender domain is in known spam list
5. **Classification**:
   - Score > 0: Classified as Phishing
   - Score = 0: Classified as Safe
6. **Display Results**: Shows classification, risk score, and detected keywords
7. **Email Report**: Optionally sends detailed analysis report to user's email

## 📊 Detection Algorithm

The detection system uses a simple but effective scoring algorithm:

```python
# Subject keywords have higher weight
if keyword_found_in_subject:
    score += 3

# Body keywords have lower weight
if keyword_found_in_body:
    score += 1

# Classification threshold
if total_score > 0:
    classification = "Phishing"
else:
    classification = "Safe"
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

- **flask**: Web framework for the application
- **requests**: HTTP library for web scraping
- **lxml**: XML/HTML processing
- **python-dotenv**: Environment variable management
- **pandas**: Data manipulation for domain analysis

## 👥 Team P5-7

Developed by Team P5-7 for INF1002 Programming Fundamentals course.