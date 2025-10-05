import os
from dotenv import load_dotenv
from datas import unique_from_emails

load_dotenv()  # Load environment variables from .env file

def domaincheck(email_title, safe_domains=unique_from_emails):
    risk_score = 0
    text = email_title.lower() #convert email text to lowercase
    start = text.find('<') + 1 #find the first character of the email address after <
    end = text.find('>', start) #it looks for > and start means it start looking from the position of start which is the first character of the email address
    email = text[start:end].strip()#extract the text between < and > and remove any leading or trailing whitespace
    domain = "@" + email.split('@', 1)[1]
    if domain in safe_domains: #check if domain is in predefined safe list
        EmailDomainMsg = f"Email is from a safe domain: {email}"
        return EmailDomainMsg, risk_score
    else:
        EmailDomainMsg = f"Warning: Email is from an unrecognized domain: {email}"
        risk_score += int(os.getenv("SENDER_KEYWORD_SCORE", "2")) #increase risk score for unrecognized domain
        return EmailDomainMsg, risk_score
    
