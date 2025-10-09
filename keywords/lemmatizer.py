"""
Purpose: 
To use a lemmatizer module to grab root words from dictionary, remove repeat words 
with similar meanings, and reduce the number of words in the dataset.

Utilise Natural Language Processing (NLP) technique but not use Machine learning (ML)
"""
import os # For file operations
from dotenv import load_dotenv # Load environment variables
import pandas as pd # For database operations
import nltk # Natural language toolkit
from nltk.stem import WordNetLemmatizer # Lemmatizer from NLTK library
from nltk.tokenize import word_tokenize # For breaking text into small chunks

# Load environment variables
load_dotenv()

# Download necessary NLTK resources
nltk.download(['punkt_tab','wordnet','averaged_perceptron_tagger'])

# Initialise lemmatiser
lemmatizer = WordNetLemmatizer()

# Define file path, find file
keywords_folder = os.getenv('KEYWORDS_FOLDER', 'keywords')
csv_file_path = os.path.join(keywords_folder, 'consolidate_keywords.csv')

# Load consolidated data CSV file 
df = pd.read_csv(csv_file_path, names=['unlem_text']) # Read CSV into DataFrame with a single column named 'unlem_text'

def get_wordnet_pos(tag):
    
    # Maps POS tag to WordNet POS tag
    tag_dict = {
        'J': nltk.corpus.wordnet.ADJ,
        'N': nltk.corpus.wordnet.NOUN,  
        'V': nltk.corpus.wordnet.VERB,
        'R': nltk.corpus.wordnet.ADV,
        'JJ': nltk.corpus.wordnet.ADJ,
        'JJR': nltk.corpus.wordnet.ADJ,
        'JJS': nltk.corpus.wordnet.ADJ,
        'VB': nltk.corpus.wordnet.VERB,
        'VBD': nltk.corpus.wordnet.VERB,
        'VBG': nltk.corpus.wordnet.VERB,
        'VBN': nltk.corpus.wordnet.VERB,
        'VBP': nltk.corpus.wordnet.VERB,
        'VBZ': nltk.corpus.wordnet.VERB
    }
    return tag_dict.get(tag[0], nltk.corpus.wordnet.NOUN)

def lemmatize_input(text):

    # Lemmatizes both single words and phrases
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Process text
    text = text.lower().strip() # Change to lowercase and then strip of all the whitespaces
    # Handle contractions
    text = text.replace("'ve", " have").replace("'s", " is").replace("'m", " am")\
              .replace("'ll", " will").replace("'d", " would").replace("'re", " are")
    tokens = word_tokenize(text) # Give a token to each word

    # If single token, lemmatize directly
    if len(tokens) == 1: 
        word = tokens[0]
        pos_tags = [nltk.corpus.wordnet.VERB, nltk.corpus.wordnet.NOUN, nltk.corpus.wordnet.ADJ, nltk.corpus.wordnet.ADV]
        
        lemmatized = word
        for pos in pos_tags:
            new_word = lemmatizer.lemmatize(word, pos=pos)
            if len(new_word) < len(lemmatized):  # Take the shortest form as it's likely more root-like
                lemmatized = new_word
            return lemmatized
    
    # If multiple tokens, get POS tags and lemmatize accordingly
    tagged = nltk.pos_tag(tokens) # Get POS tags
    lemmatized = [] # Create empty list to hold lemmatized words
    for token, pos_tag in tagged:
        pos = get_wordnet_pos(pos_tag)
        # Try multiple POS if the word doesn't change
        word = lemmatizer.lemmatize(token, pos=pos)
        if word == token and pos != nltk.corpus.wordnet.VERB:
            # Try verb form if initial lemmatization didn't change the word
            verb_form = lemmatizer.lemmatize(token, pos=nltk.corpus.wordnet.VERB)
            if len(verb_form) < len(word):  # Take shorter version as it's likely more root-like
                word = verb_form
        lemmatized.append(word)
    return ' '.join(lemmatized) # Join all lemmatized words into a single string

def process_keywords():
    # Apply lemmatization to each row
    df['lem_text'] = df['unlem_text'].apply(lemmatize_input)

    # Get the entries and sort them out and remove the empty entries
    unique_entries = sorted(set(df['lem_text'].dropna()))
    return pd.DataFrame(unique_entries, columns=['keyword'])

if __name__ == "__main__":
    # Prep output folder and file path
    output_folder = os.getenv('OUTPUT_FOLDER', 'keywords')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder) # Ensure output directory exist
    output_file_path = os.path.join(output_folder, 'lemmatized_keywords.csv')
    # Process keywords and save to CSV
    unique_df = process_keywords()
    unique_df.to_csv(output_file_path, index=False) # Save DataFrame to CSV without index
    
    