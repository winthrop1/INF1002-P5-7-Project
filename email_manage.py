import re #for regular expressions, searching patterns
import os #work with folders in file systems
#import csv #write/read data to csv file
from dotenv import load_dotenv #for loading environment variables
from datas import unique_from_emails

#load environment variables from .env file
load_dotenv()


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





r'''if __name__ == "__main__":
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
    print('='*60)'''