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

#load keywords from csv file
def load_keywords(filepath):
    keywords = [] #empty list to hold keywords
    if not os.path.exists(filepath): #check that file exsist
        print(f"Keyword file not found: {filepath}") #if not found, output not found
        return keywords #return empty list if not found
    
    with open(filepath, "r", encoding="utf-8") as file: #read the file using utf-8 encoding to handle special characters 
        for line in file: #process each line in the file
            word = line.strip() #remove whitespace
            if word: #only for non-empty lines, skips empty ones
                keywords.append(word.lower()) #make all lowercase
    return keywords #returns complete list of loaded keywords

#file paths for retrieving
#construct absolute path from environment variable or default
csv_path = os.path.join(os.path.dirname(__file__), os.getenv('KEYWORDS_CONSOLIDATE_FILE', 'keywords/lemmatized_keywords.csv'))

#load keywords from files
sus_keywords = load_keywords(csv_path)

#analyse email subject line for sus keywords
def detection_subject(subject):
    score = 0 #initialize sus score for subject line
    keywords = [] #empty list to store detected keywords
    subject_lower = subject.lower() #convert subject line to lowercase for matching

    #scan sus keywords 
    for keyword in sus_keywords:
        #create regex pattern with word boundaries to match whole words only
        #\b ensures we match "fun" but not "funny" or "unfunny"
        pattern = r'\b' + re.escape(keyword) + r'\b' #re.escape handles special regex characters in keywords
        
        #checks if keyword pattern exists in subject line
        if re.search(pattern, subject_lower):
            score += int(os.getenv("SUBJECT_KEYWORD_SCORE", "3")) #add score for subject line detection
            keywords.append(("subject", keyword)) #store tuple: (location, keyword_found)
    return score, keywords #return total score and list of detected keywords

#analyse email body for sus keywords
def detection_body(body):
    score = 0 #initialize sus score for body
    keywords = [] #empty list to store detected keywords 
    body_lower = body.lower() #convert body to lowercase for matching

    #define if found in early body is first 100 words 
    early_words_count = int(os.getenv("EARLY_BODY_WORD_COUNT", "100"))

    #spilt body in 2 
    words = body_lower.split()

    #early_words: first 100 words (phishing often front-loads suspicious content)
    early_words = ' '.join(words[:early_words_count]) if len(words) > early_words_count else body_lower
   
    #remaining_words: everything after first 100 words
    remaining_words = ' '.join(words[early_words_count:]) if len(words) > early_words_count else ""

    #go through the keywords
    for keyword in sus_keywords:
        #create regex pattern with word boundaries to match whole words only
        #\b ensures we match "fun" but not "funny" or "unfunny"
        pattern = r'\b' + re.escape(keyword) + r'\b'

        #check early body section first (higher priority/score)
        if re.search(pattern, early_words):
            score += int(os.getenv("EARLY_BODY_KEYWORD_SCORE", "2")) #add score for early body
            keywords.append(("early_body", keyword)) #store tuple: (location, keyword_found)

        #check remaining body section if keyword not found in early body
        elif remaining_words and re.search(pattern, remaining_words):
            score += int(os.getenv("BODY_KEYWORD_SCORE", "1")) #add score for remaining body
            keywords.append(("remaining_body", keyword)) #store tuple: (location, keyword_found)
    return score, keywords #return total score and list of detected keywords

#classify email as safe/phishing
def classify_email(email_subject, email_body):
    keywords_suspicion_score = 0 #initialize total sus score
    keywords = [] #list to accumulate all detected keywords from all sections

    #analyse subject line for sus keywords
    subject_score, subject_keywords = detection_subject(email_subject) #detect suspicious keywords in subject
    keywords_suspicion_score += subject_score #add subject score to total
    keywords.extend(subject_keywords) #append keywords to list

    #analyze email body for sus keywords
    body_score, body_keywords = detection_body(email_body) #detect suspicious keywords in body
    keywords_suspicion_score += body_score #add body score to total
    keywords.extend(body_keywords) #append keywords to list

    return keywords, keywords_suspicion_score #output score with keywords

#test execution block - only runs when script is executed directly
if __name__ == "__main__":
    #placeholder for testing the consolidate_csv_keywords function
    print("Running consolidate_csv_keywords function...")
    consolidate_csv_keywords()
