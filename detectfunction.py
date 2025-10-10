import re #for regular expressions, searching patterns
import os #work with folders in file systems
#import csv #write/read data to csv file
from dotenv import load_dotenv #for loading environment variables
from datas import unique_from_emails

#load environment variables from .env file
load_dotenv()

#load keywords from txt file
def load_keywords(filepath):
    keywords = [] #empty list to hold keywords
    if not os.path.exists(filepath): #check that file exsist
        print(f"Keyword file not found: {filepath}") #if not found, output not found
        return keywords #return empty list if not found
    
    with open(filepath, "r", encoding="utf-8") as file: #read the file using utf-8 encoding 
        for line in file:
            word = line.strip() #remove whitespace
            if word: 
                keywords.append(word.lower()) #make all lowercase
    return keywords

#load keywords from csv file
# def load_keywords(filepath):
#     keywords = []
#     if not os.path.exists(filepath):
#         print(f"Keyword file not found: {filepath}")
#         return keywords
#     with open(filepath, "r", encoding="utf-8") as file:
#         reader = csv.reader(file)
#         header = next(reader, None)  # skip header
#         for row in reader:
#             if row:
#                 keywords.append(row[0].lower())
#     return keywords

#file paths for retrieving
#construct absolute path from environment variable or default
txt_path = os.path.join(os.path.dirname(__file__), os.getenv('SPAM_WORDS_PATH', 'words/spam_words.txt'))
# csv_path = os.path.join(os.path.dirname(__file__), "words", "spam_words.csv")

#load keywords from files
sus_keywords = load_keywords(txt_path)
# sus_keywords = load_keywords(csv_path)

def parse_email_file(email_content):
    """
    Parse decoded email content and separate into different parts.
    Takes the decoded message string from website and returns separated components.

    Args:
        email_content (str): Decoded email content from Flask file upload

    Returns:
        tuple: (title, subject, body) as strings
    """
    try:
        from email import message_from_string

        title = ""
        subject = ""
        body = ""

        # Check if it's an .eml format (structured email with headers)
        if "From:" in email_content and "To:" in email_content:
            msg = message_from_string(email_content)

            # Extract subject
            subject = msg.get('Subject', '')

            # Create title from sender info
            from_field = msg.get('From', 'Unknown')
            title = f"Email from {from_field}"

            # Extract body content
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)
                        if isinstance(body, bytes):
                            body = body.decode('utf-8', errors='ignore')
                        break
            else:
                payload = msg.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body = payload.decode('utf-8', errors='ignore')
                else:
                    body = str(payload)
        else:
            # Handle plain text format (simple emails)
            lines = email_content.splitlines()

            # Look for subject line
            for i, line in enumerate(lines):
                if line.lower().startswith('subject:'):
                    subject = line[8:].strip()  # Remove "Subject:" prefix
                    title = f"Email - {subject[:50]}..." if len(subject) > 50 else f"Email - {subject}"
                    # Rest of the content is body
                    body = '\n'.join(lines[i+1:]).strip()
                    break

            # If no subject found, treat whole content as body
            if not subject:
                body = email_content.strip()
                title = "Email Content"
                subject = "No Subject"

        return title, subject, body

    except Exception as e:
        print(f"Error parsing email content: {e}")
        return "Error", "Error parsing email", "Could not parse email content"
    
#detect keywords from email text
def detection_subject(subject):
    score = 0 #assign scores
    keywords = []
    subject_lower = subject.lower() #convert subject to lowercase incase of case-sensitive match

    for keyword in sus_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b' #regex pattern to match whole word
        if re.search(pattern, subject_lower):
            score += 3 #higher weight for sus words in subject
            keywords.append(f"Suspicious word in subject: '{keyword}'")
    return score, keywords #ouput total scoore with keywords

#score the keywoprds based on their position subject or body
def detection_body(body):
    score = 0
    keywords = []
    body_lower = body.lower() #convert body to lowercase incase of case-sensitive match

    for keyword in sus_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b' #regex pattern to match whole word
        if re.search(pattern, body_lower):
            score += 1 #lower weight for sus in body
            keywords.append(f"Suspicious word in body: '{keyword}'")
    return score, keywords #ouput total scoore with keywords

#classify email as safe/phishing
def classify_email(email_subject, email_body):
    total_score = 0
    keywords = []

    #s = score, k = keyword
    s, k = detection_subject(email_subject) #detect suspicious keywords in subject
    total_score += s #addscore to total
    keywords.extend(k) #append keywords

    s, k = detection_body(email_body) #detect suspicious keywords in body
    total_score += s #add score to total
    keywords.extend(k) #append keywords

    classification = "Safe" if total_score == 0 else "Phishing"
    return classification, keywords, total_score #output score with keywords

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
        risk_score += 2 #increase risk score for unrecognized domain
        return EmailDomainMsg, risk_score


if __name__ == "__main__":
    # Test file paths
    test_files = ["spam/spam_1.txt", "ham/ham_1.txt"]

    for filepath in test_files:
        print(f"\n{'='*60}")
        print(f"Testing file: {filepath}")
        print('='*60)

        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' not found")
            continue

        try:
            # Read and decode file (simulating Flask upload)
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()

            print(f"Original file content (first 200 chars):\n{file_content[:200]}...\n")

            # Test parse_email_file function
            title, subject, body = parse_email_file(file_content)

            print("PARSED EMAIL COMPONENTS:")
            print(f"Title: {title}")
            print(f"Subject: {subject}")
            print(f"Body (first 150 chars): {body[:150]}...")

            # Test classification with original content
            classification, keywords, total_score = classify_email(subject, body)

            print(f"\nCLASSIFICATION RESULTS:")
            print(f"Classification: {classification}")
            print(f"Risk Score: {total_score}")

            if keywords:
                print("Suspicious keywords detected:")
                for keyword in keywords:
                    print(f"  - {keyword}")
            else:
                print("No suspicious keywords detected.")

        except Exception as e:
            print(f"Error processing file: {e}")

    print(f"\n{'='*60}")
    print("Testing completed!")
    print('='*60)