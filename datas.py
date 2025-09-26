import pandas as pd
import string
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get spam directory from environment variable or use default
ham_dir = os.getenv('SPAM_DATASET_DIR', 'hamEmails/')


def load_data(directory, label):
    texts = []
    labels = []
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), 'r', encoding='latin1') as file:
            texts.append(file.read())  # Read the content of the email file
            labels.append(label)  # Assign the provided label (1 for spam, 0 for ham)
    return texts, labels

ham_texts, ham_labels = load_data(ham_dir, 1)  # 1 for spam


# Combine all data and labels into one dataset
texts = ham_texts 
labels = ham_labels

# Create a DataFrame
emailDataF = pd.DataFrame({'text': texts, 'label': labels})

def list_of_domains(text):
    domains = []
    lines = text.splitlines() #Split text into individual lines
    for line in lines: 
        if "from" in line.lower() or "from:" in line.lower(): # Look for 'from' 
            words = line.split() # Split the line into a list of words
            for word in words:
                if "@" in word: # Look for '@' symbol in each word
                    clean_word = word.strip(string.punctuation) # Extract domain part and remove punctuation
                    parts = clean_word.split('@')
                    if len(parts) == 2:
                        domain = "@" + parts[1] #split the clean_word into half and get domain after the @ symbol
                        domains.append(domain)

    return domains


emailDomains = emailDataF['text'].apply(list_of_domains).tolist() # Apply the function to the 'text' column to get a list of domains for each email
all_from_emails = [email for sublist in emailDomains for email in sublist] # Flatten the list of lists (goes through each sublist and through each email in the sublist and adds it to the main list)
unique_from_emails = set(all_from_emails) #Remove any duplicates