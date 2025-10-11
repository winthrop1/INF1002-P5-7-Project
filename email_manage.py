import re #for regular expressions, searching patterns
import os #work with folders in file systems
#import csv #write/read data to csv file
from dotenv import load_dotenv #for loading environment variables
from datas import unique_from_emails

#load environment variables from .env file
load_dotenv()

def parse_email_file(email_content):
    """
    Parse decoded email content and separate into different parts.
    Takes the decoded message string from website and returns separated components.
    - title: A brief title for the email (e.g., "Email from
    - subject: <subject line>")
    - body: The main content of the email
    """
    try:
        from email import message_from_string

        title = ""
        subject = ""
        body = ""

        # Check if it's an .eml format
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
            # Handle plain text format
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

if __name__ == "__main__":
    # Test file paths for email parsing functionality
    test_file = os.getenv("TEST_EMAIL_FILE", "dataset/testing/spam_1.txt")

    print("Testing parse_email_file function")
    print("="*50)

    print(f"\nTesting file: {test_file}")
    print('-'*30)

    # Check if file exists
    if not os.path.exists(test_file):
        print(f"Error: File '{test_file}' not found")

    try:
        # Read and decode file (simulating Flask upload)
        with open(test_file, 'r', encoding='utf-8') as f:
            file_content = f.read()

        print(f"Original content preview: {file_content[:100]}...")

        # Test parse_email_file function
        title, subject, body = parse_email_file(file_content)

        print("\nParsed Email Components:")
        print(f"  Title: {title}")
        print(f"  Subject: {subject}")
        print(f"  Body preview: {body[:100]}...")

        # Show parsing success
        print("  ✓ Email parsing successful")

    except Exception as e:
        print(f"  ✗ Error parsing email: {e}")

    print(f"\n{'='*50}")
    print("Email parsing test completed!")
    print('='*50)