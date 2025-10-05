import re #for regular expressions, searching patterns
import os #work with folders in file systems
import csv #write/read data to csv file
import pandas as pd
from typing import Set, List
from dotenv import load_dotenv

load_dotenv()  #for loading environment variables

def consolidate_csv_keywords() -> None:
    """
    Load keywords from all CSV files 
    and consolidate them into a single CSV file.

    Removes duplicates and sorts the keywords alphabetically.
    """
    raw_data_dir = os.getenv('KEYWORDS_RAW_FOLDER', 'keywords/raw_data')
    output_folder = os.getenv('KEYWORDS_FOLDER', 'keywords')
    output_file = os.path.join(output_folder, 'consolidate_keywords.csv')

    # Check if raw_data directory exists
    if not os.path.exists(raw_data_dir):
        print(f"Error: Directory {raw_data_dir} does not exist")
        return

    # Get all CSV files in the raw_data directory
    csv_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.csv')]

    if not csv_files:
        print(f"No CSV files found in {raw_data_dir}")
        return

    print(f"Found {len(csv_files)} CSV files: {csv_files}")

    # Set to store unique keywords
    all_keywords: Set[str] = set()

    # Process each CSV file
    for csv_file in csv_files:
        file_path = os.path.join(raw_data_dir, csv_file)
        print(f"Processing: {csv_file}")

        try:
            # Try reading with pandas first (handles headers automatically)
            df = pd.read_csv(file_path)

            # Extract all non-null values from all columns
            for column in df.columns:
                keywords = df[column].dropna().astype(str).str.strip()
                # Filter out empty strings and header-like values
                keywords = keywords[keywords != '']
                keywords = keywords[~keywords.str.contains('^#|spam_words|keyword', case=False, na=False)]
                all_keywords.update(keywords.tolist())

        except Exception as e:
            print(f"Error reading {csv_file} with pandas, trying manual parsing: {e}")

    # Remove any remaining unwanted entries
    filtered_keywords = {kw for kw in all_keywords if kw and len(kw.strip()) > 0}

    # Convert to sorted list
    sorted_keywords: List[str] = sorted(filtered_keywords)

    print(f"Total unique keywords collected: {len(sorted_keywords)}")

    # Write consolidated keywords to CSV
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for keyword in sorted_keywords:
                writer.writerow([keyword])

        print(f"Successfully created {output_file} with {len(sorted_keywords)} keywords")

    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

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
csv_path = os.path.join(os.path.dirname(__file__), os.getenv('KEYWORDS_CONSOLIDATE_PATH', 'keywords/consolidate_keywords.csv'))

#load keywords from files
sus_keywords = load_keywords(csv_path)


def detection_subject(subject):
    score = 0 #assign scores
    keywords = []
    subject_lower = subject.lower() #convert subject to lowercase in case of case-sensitive match

    for keyword in sus_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b' #regex pattern to match whole word
        if re.search(pattern, subject_lower):
            score += int(os.getenv("SUBJECT_KEYWORD_SCORE", "3"), ) #higher weight for sus words in subject
            keywords.append(f"Suspicious word in subject: '{keyword}'")
    return score, keywords #output total score with keywords

#score the keywords based on their position subject or body
def detection_body(body):
    score = 0
    keywords = []
    body_lower = body.lower() #convert body to lowercase incase of case-sensitive match
    early_words_count = int(os.getenv("EARLY_BODY_WORD_COUNT", "100")) #number of words to check for early keywords

    # Split body into words and find the position of early words
    words = body_lower.split()
    early_words = ' '.join(words[:early_words_count]) if len(words) > early_words_count else body_lower
    remaining_words = ' '.join(words[early_words_count:]) if len(words) > early_words_count else ""

    for keyword in sus_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b' #regex pattern to match whole word

        # Check if keyword is in early email words
        if re.search(pattern, early_words):
            score += int(os.getenv("EARLY_BODY_KEYWORD_SCORE", "2")) #higher weight for early sus words
            keywords.append(f"Suspicious word in early body: '{keyword}'")
        # Check if keyword is in remaining words (after early detection)
        elif remaining_words and re.search(pattern, remaining_words):
            score += int(os.getenv("BODY_KEYWORD_SCORE", "1")) #lower weight for remaining sus words
            keywords.append(f"Suspicious word in remaining body: '{keyword}'")
    return score, keywords #ouput total scoore with keywords

#classify email as safe/phishing
def classify_email(email_subject, email_body):
    total_score = 0
    keywords_suspicion_score = 0
    keywords = []

    #s = score, k = keyword
    s, k = detection_subject(email_subject) #detect suspicious keywords in subject
    keywords_suspicion_score += s #add score to total
    keywords.extend(k) #append keywords

    s, k = detection_body(email_body) #detect suspicious keywords in body
    keywords_suspicion_score += s #add score to total
    keywords.extend(k) #append keywords

    classification = "Safe" if total_score == 0 else "Phishing"
    return classification, keywords, total_score #output score with keywords


if __name__ == "__main__":
    # Test the consolidate_csv_keywords function
    print("Running consolidate_csv_keywords function...")
    consolidate_csv_keywords()
