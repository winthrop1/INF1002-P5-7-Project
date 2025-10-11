import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read logging configuration from environment
ENABLE_LOGGING = os.getenv('ENABLE_LOGGING', 'true').lower() == 'true'
LOG_FOLDER = os.getenv('LOG_FOLDER', 'log')
LOG_FILE = os.getenv('LOG_FILE', 'phishing_detector.log')
FULL_LOG_PATH = os.path.join(LOG_FOLDER, LOG_FILE)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Extract logger name from log file (remove .log extension)
LOGGER_NAME = os.getenv('LOGGER_NAME', os.path.splitext(LOG_FILE)[0])

# Create logger
logger = logging.getLogger(LOGGER_NAME)

def setup_logging():
    # Setup logging configuration
    if not ENABLE_LOGGING:
        return

    # Create log directory
    os.makedirs(LOG_FOLDER, exist_ok=True)

    # Avoid duplicate handlers
    if logger.handlers:
        return

    # Create file handler for our specific logger only
    file_handler = logging.FileHandler(FULL_LOG_PATH, encoding='utf-8')
    file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))

    # Add handler to logger only
    logger.addHandler(file_handler)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Prevent propagation to root logger
    logger.propagate = False

def log_analysis(filename, runtime, classification, risk_level, total_risk_scoring,
                 domain_capped, url_capped, keywords_capped, keywords_count,
                 number_of_urls, number_of_unique_domains, url_reason_pairs,
                 EmailDomainMsg):
    """Log email analysis results"""
    if not ENABLE_LOGGING:
        return

    # Prepare URL analysis summary (avoid logging full URLs with potential credentials)
    url_analysis_summary = f"{number_of_urls} URLs analyzed, {number_of_unique_domains} unique domains"
    if url_reason_pairs:
        # Log only the reasons, not the full URLs
        url_reasons_list = [d.get('reason', 'N/A') for d in url_reason_pairs]
        url_analysis_summary += f" | Flags: {', '.join(set(url_reasons_list))}"

    # Log comprehensive analysis information (using lazy logging)
    logger.info(
        "File: %s | Runtime: %.4fs | Classification: %s | "
        "Risk: %s (%s) | Domain Score: %s | "
        "URL Score: %s | Keyword Score: %s | "
        "Keywords Found: %s | %s | Domain Check: %s",
        filename, runtime, classification,
        risk_level, total_risk_scoring, domain_capped,
        url_capped, keywords_capped,
        keywords_count, url_analysis_summary, EmailDomainMsg
    )

def log_admin_login_success():
    """Log successful admin login"""
    if ENABLE_LOGGING:
        logger.info("Admin login successful")

def log_admin_login_failure():
    """Log failed admin login attempt"""
    if ENABLE_LOGGING:
        logger.warning("Failed admin login attempt")

def log_admin_logout():
    """Log admin logout"""
    if ENABLE_LOGGING:
        logger.info("Admin logout")

def log_email_sent():
    """Log successful email report sending"""
    if ENABLE_LOGGING:
        logger.info("Email report sent successfully")

def log_email_failed(error_type):
    """Log failed email report sending"""
    if ENABLE_LOGGING:
        logger.error("Failed to send email report: %s", error_type)

def log_data_storage_success():
    """Log successful data storage"""
    if ENABLE_LOGGING:
        logger.info("Analysis data stored successfully")
