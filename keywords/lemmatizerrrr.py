"""
Purpose: 
To use a lemmatizer module to grab root words from dictionary, remove repeat words 
with similar meanings, and reduce the number of words in the dataset.

Utilise Natural Language Processing (NLP) technique
"""
import os
from dotenv import load_dotenv
import pandas as pd
import nltk 
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Load environment variables
load_dotenv()

# Download necessary NLTK resources
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Initialise lemmatiser
lemmatizer = WordNetLemmatizer()

# Define file path, find file
keywords_folder = os.getenv('KEYWORDS_FOLDER', 'keywords')
csv_file_path = os.path.join(keywords_folder, 'consolidate_keywords.csv')

# Load consolidated data CSV file 
df = pd.read_csv(csv_file_path, names=['unlem_text']) # Read CSV into DataFrame with a single column named 'unlem_text'

# A function to assign each word with grammatical categories
def get_wordnet_pos(word, tag):
    tag_dict = {
        'J': nltk.corpus.wordnet.ADJ,
        'N': nltk.corpus.wordnet.NOUN,  
        'V': nltk.corpus.wordnet.VERB,
        'R': nltk.corpus.wordnet.ADV
    }
    return tag_dict.get(tag[0], nltk.corpus.wordnet.NOUN) # Default to NOUN if tag not found

# Function to lemmatize txt in each row
def lemmatize_text(text):
    tokens = word_tokenize(str(text).lower()) # Tokenize and convert to lowercase for each cell
    tagged = nltk.pos_tag(tokens) # Get POS tags for tokens
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens] # Lemmatize each word in the text
    return ' '.join(lemmatized_tokens) # Join back into a single string

# Apply lemmatization to the 'text' column
df['lem_text'] = df['unlem_text'].apply(lemmatize_text)

# Save the updated DataFrame to a new CSV file
df[['lem_text']].to_csv(os.path.join(keywords_folder, 'lemmatized_keywords.csv'), index=False)