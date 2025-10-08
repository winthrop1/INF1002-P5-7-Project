"""
Purpose: 
To use a lemmatizer module to grab root words from dictionary, remove repeat words 
with similar meanings, and reduce the number of words in the dataset.

Utilise Natural Language Processing (NLP) technique but not use Machine learning (ML)
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
nltk.download('punkt_tab') # Tokeniser (identify words and sentences in text)
nltk.download('wordnet') # References dictionary for lemmatization
nltk.download('averaged_perceptron_tagger') # Used for assigning parts of speech to words, pre-trained model

# Initialise lemmatiser
lemmatizer = WordNetLemmatizer()

# Define file path, find file
keywords_folder = os.getenv('KEYWORDS_FOLDER', 'keywords')
csv_file_path = os.path.join(keywords_folder, 'consolidate_keywords.csv')

# Load consolidated data CSV file 
df = pd.read_csv(csv_file_path, names=['unlem_text']) # Read CSV into DataFrame with a single column named 'unlem_text'

# A function to assign each word with grammatical categories
def get_wordnet_pos(tag):
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
    lemmatized_tokens = [lemmatizer.lemmatize(token, get_wordnet_pos(pos_tag)) for token, pos_tag in tagged] # Unpack (token, pos_tag) from tagged
    return ' '.join(lemmatized_tokens) # Join back into a single string

# Apply lemmatization to dataframe
df['lem_text'] = df['unlem_text'].apply(lemmatize_text) # Apply lemmatization function to each row in 'unlem_text' column

# Split lemmatized phrase into words
split_phrases = df['lem_text'].str.split()

# Flatten list & split words into individual words
all_words = [word for phrase in split_phrases for word in phrase]

# Remove duplicates & sort words
remove_duplicates = sorted(set(all_words))

# Prep output folder and file path
output_folder = os.getenv('OUTPUT_FOLDER', 'keywords')
if not os.path.exists(output_folder):
    os.makedirs(output_folder) # Ensure output directory exist
output_file_path = os.path.join(output_folder, 'lemmatized_keywords.csv')

# Save to CSV 
unique_df = pd.DataFrame(remove_duplicates, columns=['keyword'])
unique_df.to_csv(output_file_path, index=False) # Save DataFrame to CSV without index