import datas
import os
import email_manage
import keyword_scrape_web
from email_manage import parse_email_file
from suspiciouswords import classify_email
from domainchecker import domaincheck
from suspiciousurl import calling_all_functions, assessing_risk_scores, get_urls_from_email_file
from domainchecker import domaincheck

final_score = 0

def process_email_file(email_file):
    
    get_urls_from_email_file(email_file)

    # Parse email using the parse_email_file function
    email_title, email_subject, email_body = parse_email_file(email_file) 

    # Domain check
    EmailDomainMsg, risk_score = domaincheck(email_title)

    calling_all_functions()
    assessing_risk_scores()

    # Classify the email using the keyword detection system
    classification, keywords, total_score = classify_email(email_subject, email_body)
file_path = r"C:\Users\User\Documents\GitHub\INF1002-P5-7-Project\spam\spam_1.txt" 





if __name__ == "__main__":
    
    email_file = os.path.join(os.path.dirname(__file__), os.getenv("TEST_EMAIL_FILE"), "dataset/testing/spam_1.txt") # Placeholder for user input email file content
    process_email_file(email_file)
    
