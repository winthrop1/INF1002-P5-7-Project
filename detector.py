import re #for regular expressions, searching patterns
import os #work with folders in file systems
#import csv #write/read data to csv file
from dotenv import load_dotenv #for loading environment variables

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
def classify_email(email_text):
    total_score = 0
    keywords = []

    #extract subject from the email 
    subject_match = re.search(r"Subject: (.*)", email_text, re.IGNORECASE)
    #extract subject but if dont have set empty
    if subject_match:
        subject = subject_match.group(1)
    else:
        subject = "" 
    body = email_text

    #s = score, k = keyword
    s, k = detection_subject(subject) #detect suspicious keywords in subject
    total_score += s #addscore to total
    keywords.extend(k) #append keywords

    s, k = detection_body(body) #detect suspicious keywords in body
    total_score += s #add score to total
    keywords.extend(k) #append keywords

    classification = "Safe" if total_score == 0 else "Phishing"
    return classification, keywords, total_score #output score with keywords

if __name__ == "__main__":
    from email import message_from_string

    # Specify the file path to test
    filepath = "spam/spam_1.txt"  # Change this to test different files

    # Check if file exists
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found")
    else:
        # Read the file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()

            # Handle .eml files
            if filepath.lower().endswith('.eml'):
                msg = message_from_string(file_content)
                subject = msg.get('Subject', '')
                body = ''

                # Extract body from email message
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                email_text = f"Subject: {subject}\n{body}"
            else:
                # For .txt files, use content as-is
                email_text = file_content

            # Classify the email using the classify_email function
            classification, keywords, total_score = classify_email(email_text)

            # Display results
            print(f"\nFile: {filepath}")
            print(f"Classification: {classification}")
            print(f"Risk Score: {total_score}")

            if keywords:
                print("\nSuspicious keywords detected:")
                for keyword in keywords:
                    print(f"  - {keyword}")
            else:
                print("\nNo suspicious keywords detected.")

        except Exception as e:
            print(f"Error reading file: {e}")