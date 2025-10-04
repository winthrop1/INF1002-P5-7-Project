import re #for regular expressions, searching patterns
import os #work with folders in file systems
#import csv #write/read data to csv file
from dotenv import load_dotenv


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



#file paths for retrieving
#construct absolute path from environment variable or default
txt_path = os.path.join(os.path.dirname(__file__), os.getenv('SPAM_WORDS_PATH', 'words/spam_words.txt'))
# csv_path = os.path.join(os.path.dirname(__file__), "words", "spam_words.csv")

#load keywords from files
sus_keywords = load_keywords(txt_path)
# sus_keywords = load_keywords(csv_path)



def detection_subject(subject):
    score = 0 #assign scores
    keywords = []
    subject_lower = subject.lower() #convert subject to lowercase in case of case-sensitive match

    for keyword in sus_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b' #regex pattern to match whole word
        if re.search(pattern, subject_lower):
            score += 3 #higher weight for sus words in subject
            keywords.append(f"Suspicious word in subject: '{keyword}'")
    return score, keywords #output total score with keywords

#score the keywords based on their position subject or body
def detection_body(body):
    score = 0
    keywords = []
    body_lower = body.lower() #convert body to lowercase incase of case-sensitive match

    for keyword in sus_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b' #regex pattern to match whole word
        if re.search(pattern, body_lower):
            score += 1 #lower weight for sus in body
            keywords.append(f"Suspicious word in body: '{keyword}'")
    return score, keywords #output total score with keywords

#classify email as safe/phishing
def classify_email(email_subject, email_body):
    keywords_suspicion_score = 0
    keywords = []

    #s = score, k = keyword
    s, k = detection_subject(email_subject) #detect suspicious keywords in subject
    keywords_suspicion_score += s #add score to total
    keywords.extend(k) #append keywords

    s, k = detection_body(email_body) #detect suspicious keywords in body
    keywords_suspicion_score += s #add score to total
    keywords.extend(k) #append keywords

    classification = "Safe" if keywords_suspicion_score == 0 else "Phishing"
    return classification, keywords, keywords_suspicion_score #output score with keywords