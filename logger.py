"""
Logging module for Phishing Email Detection System
Handles all logging configuration and log message formatting
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read logging configuration from environment
ENABLE_LOGGING = os.getenv('ENABLE_LOGGING', 'true').lower() == 'true'
LOG_FOLDER = os.getenv('LOG_FOLDER', 'log')
LOG_FILE = os.getenv('LOG_FILE', 'phishing_detector.log')
FULL_LOG_PATH = os.path.join(LOG_FOLDER, LOG_FILE)

def setup_logging():
    """
    Configure logging based on environment variables
    Creates log directory if it doesn't exist
    """
    if ENABLE_LOGGING:
        os.makedirs(LOG_FOLDER, exist_ok=True)

def _write_log(level, message):
    """Write a log message to file without using Python's logging module"""
    if not ENABLE_LOGGING:
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
    log_entry = f"{timestamp} - {level} - {message}\n"

    try:
        with open(FULL_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception:
        pass  # Silently fail if logging doesn't work

def log_analysis(filename, runtime, classification, risk_level, total_risk_scoring,
                 domain_capped, url_capped, keywords_capped, keywords_count,
                 number_of_urls, number_of_unique_domains, url_reason_pairs,
                 EmailDomainMsg):
    """
    Log email analysis results

    Args:
        filename: Name of the uploaded email file
        runtime: Analysis runtime in seconds
        classification: Safe or Phishing
        risk_level: Risk level (VERY HIGH, HIGH, MEDIUM, LOW, VERY LOW)
        total_risk_scoring: Total risk score
        domain_capped: Capped domain score
        url_capped: Capped URL score
        keywords_capped: Capped keyword score
        keywords_count: Number of keywords found
        number_of_urls: Number of URLs analyzed
        number_of_unique_domains: Number of unique domains
        url_reason_pairs: List of URL analysis results
        EmailDomainMsg: Domain check message
    """
    if not ENABLE_LOGGING:
        return

    # Prepare URL analysis summary (avoid logging full URLs with potential credentials)
    url_analysis_summary = f"{number_of_urls} URLs analyzed, {number_of_unique_domains} unique domains"
    if url_reason_pairs:
        # Log only the reasons, not the full URLs
        url_reasons_list = [d.get('reason', 'N/A') for d in url_reason_pairs]
        url_analysis_summary += f" | Flags: {', '.join(set(url_reasons_list))}"

    # Log comprehensive analysis information
    message = (
        f"File: {filename} | Runtime: {runtime:.4f}s | Classification: {classification} | "
        f"Risk: {risk_level} ({total_risk_scoring}) | Domain Score: {domain_capped} | "
        f"URL Score: {url_capped} | Keyword Score: {keywords_capped} | "
        f"Keywords Found: {keywords_count} | {url_analysis_summary} | Domain Check: {EmailDomainMsg}"
    )
    _write_log("INFO", message)

def log_admin_login_success():
    """Log successful admin login"""
    _write_log("INFO", "Admin login successful")

def log_admin_login_failure():
    """Log failed admin login attempt"""
    _write_log("WARNING", "Failed admin login attempt")

def log_admin_logout():
    """Log admin logout"""
    _write_log("INFO", "Admin logout")

def log_email_sent():
    """Log successful email report sending"""
    _write_log("INFO", "Email report sent successfully")

def log_email_failed(error_type):
    """Log failed email report sending"""
    _write_log("ERROR", f"Failed to send email report: {error_type}")

def log_data_storage_success():
    """Log successful data storage"""
    _write_log("INFO", "Analysis data stored successfully")
