import os
import re
import csv
import glob
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def extract_email_content(file_path):
    """
    Extract subject and body content from an email file.
    Skips headers and focuses on the actual message content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()

        # Find the end of headers (empty line)
        header_end = content.find('\n\n')
        if header_end == -1:
            header_end = content.find('\r\n\r\n')

        if header_end != -1:
            headers = content[:header_end]
            body = content[header_end:].strip()
        else:
            # If no clear header separation, treat entire content as body
            headers = ""
            body = content

        # Extract subject from headers
        subject = ""
        subject_match = re.search(r'^Subject:\s*(.*)$', headers, re.MULTILINE | re.IGNORECASE)
        if subject_match:
            subject = subject_match.group(1).strip()

        return subject + " " + body

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def clean_text(text):
    """
    Clean and normalize text for word frequency analysis.
    """
    # Convert to lowercase
    text = text.lower()

    # Remove HTML tags and content
    text = re.sub(r'<[^>]+>', '', text)

    # Remove common HTML entities and artifacts
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'nbsp|quot|amp|lt|gt', '', text)

    # Remove email headers artifacts, URLs, and email addresses
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[<>]', '', text)

    # Keep only alphabetic characters and spaces
    text = re.sub(r'[^a-z\s]', ' ', text)

    # Remove extra whitespace
    text = ' '.join(text.split())

    return text

def get_words(text):
    """
    Extract words from text, filtering out common stop words and short words.
    """
    # Common stop words and HTML artifacts to exclude
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has',
        'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
        'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'am', 'if', 'so',
        'no', 'not', 'only', 'own', 'same', 'such', 'than', 'too', 'very',
        'just', 'now', 'get', 'all', 'any', 'from', 'up', 'out', 'about',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'among', 'until', 'while', 'since', 'because', 'although',
        'unless', 'where', 'when', 'why', 'how', 'what', 'who', 'which', 'whom',
        # HTML and email artifacts
        'font', 'size', 'nbsp', 'color', 'style', 'div', 'span', 'table', 'tr', 'td',
        'html', 'body', 'head', 'title', 'meta', 'link', 'script', 'img', 'src',
        'alt', 'width', 'height', 'border', 'cellpadding', 'cellspacing', 'align',
        'valign', 'bgcolor', 'class', 'type', 'href', 'target', 'blank', 'text',
        # Email headers
        'received', 'from', 'subject', 'date', 'message', 'reply', 'return', 'path'
    }

    words = text.split()

    # Filter out stop words and words shorter than 3 characters
    filtered_words = [
        word for word in words
        if len(word) >= 3 and word not in stop_words
    ]

    return filtered_words

def analyze_spam_directory(directory_path):
    """
    Analyze all email files in the specified directory and get top 3 words from each file.
    Returns a list of dictionaries with filename and top words.
    """
    results = []
    processed_files = 0
    total_files = 0

    # Count total files for progress tracking
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            total_files += 1

    print(f"Processing {total_files} email files for individual analysis...")

    # Process each file
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if os.path.isfile(file_path):
            # Extract email content
            email_content = extract_email_content(file_path)

            if email_content:
                # Clean and extract words
                cleaned_text = clean_text(email_content)
                words = get_words(cleaned_text)

                if words:  # Only process files that have words
                    # Count words in this specific file
                    file_word_counter = Counter(words)

                    # Get top 2 words for this file, excluding words with frequency of 1
                    top_words = file_word_counter.most_common()

                    # Filter out words with frequency of 1 and take top 2
                    filtered_words = [(word, freq) for word, freq in top_words if freq > 1][:2]

                    # Add results for each top word
                    for word, frequency in filtered_words:
                        results.append({
                            'word': word,
                            'frequency': frequency
                        })

            processed_files += 1
            if processed_files % 100 == 0:
                print(f"Processed {processed_files}/{total_files} files...")

    print(f"Completed processing {processed_files} files.")
    return results

def save_per_file_results_to_csv(results, output_file):
    """
    Save per-file top words results to a CSV file.
    """
    # Write to CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Word', 'Frequency'])  # Header

        for result in results:
            writer.writerow([
                result['word'],
                result['frequency']
            ])

    print(f"\nTop 2 words per file analysis saved to {output_file}")

    # Print summary statistics
    total_entries = len(results)
    print(f"Summary: {total_entries} word entries")

    # Show first few examples
    if results:
        print(f"\nFirst few entries:")
        for i, result in enumerate(results[:6]):  # Show first 6 entries
            print(f"'{result['word']}' - {result['frequency']} times")
            if i == 5:
                break

def find_existing_csv(search_folder, pattern="top_2_words_spam_*.csv"):
    """
    Find the most recent CSV file matching the pattern in the search folder.
    Returns the file path if found, None otherwise.
    """
    search_path = os.path.join(search_folder, pattern)
    matching_files = glob.glob(search_path)

    if not matching_files:
        return None

    # Get the most recent file based on modification time
    most_recent = max(matching_files, key=os.path.getmtime)
    return most_recent

def load_existing_csv(file_path):
    """
    Load existing CSV data and return as a dictionary {word: frequency}.
    """
    word_freq_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                word = row['Word'].strip().lower()
                frequency = int(row['Frequency'])
                word_freq_dict[word] = frequency
        print(f"Loaded {len(word_freq_dict)} existing words from {file_path}")
    except Exception as e:
        print(f"Error loading existing CSV: {e}")

    return word_freq_dict

def merge_word_data(existing_data, new_results):
    """
    Merge new results with existing data, summing frequencies for duplicate words.
    Returns merged dictionary {word: frequency}.
    """
    merged_data = existing_data.copy()

    for result in new_results:
        word = result['word'].lower()
        frequency = result['frequency']

        if word in merged_data:
            merged_data[word] += frequency
        else:
            merged_data[word] = frequency

    return merged_data

def save_merged_results_to_csv(merged_data, output_file):
    """
    Save merged word frequency data to CSV file.
    """
    # Sort by frequency (descending) then by word (ascending)
    sorted_items = sorted(merged_data.items(), key=lambda x: (-x[1], x[0]))

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Word', 'Frequency'])  # Header

        for word, frequency in sorted_items:
            writer.writerow([word, frequency])

    print(f"\nMerged results saved to {output_file}")
    print(f"Total unique words: {len(merged_data)}")

def main():
    """
    Main function to run the per-file word frequency analysis.
    """
    # Directory containing spam emails
    spam_directory = os.getenv('SPAM_SOURCE_PATH', 'dataset/spam_2')

    # Output folder (change this to save CSV to a different folder)
    output_folder = os.getenv('OUTPUT_FOLDER', 'keywords')

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Check if spam directory exists
    if not os.path.exists(spam_directory):
        print(f"Error: Directory '{spam_directory}' not found.")
        return

    # Look for existing CSV files in the output folder
    existing_csv = find_existing_csv(output_folder)
    existing_data = {}

    if existing_csv:
        print(f"Found existing CSV: {existing_csv}")
        existing_data = load_existing_csv(existing_csv)
    else:
        print("No existing CSV files found. Creating new file.")

    # Analyze the spam directory for per-file results
    print("Starting per-file word frequency analysis for top 2 words...")
    new_results = analyze_spam_directory(spam_directory)

    if not new_results:
        print("No new words found in the emails.")
        if not existing_data:
            print("No data to save.")
            return

    # Merge new results with existing data
    merged_data = merge_word_data(existing_data, new_results)

    # Generate timestamped output CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = os.path.join(output_folder, f"top_2_words_spam_{timestamp}.csv")

    # Save merged results
    save_merged_results_to_csv(merged_data, output_csv)

    # Remove old file if it exists (since we've created a new timestamped version)
    if existing_csv and os.path.exists(existing_csv):
        try:
            os.remove(existing_csv)
            print(f"Removed old file: {existing_csv}")
        except Exception as e:
            print(f"Warning: Could not remove old file {existing_csv}: {e}")

    print(f"\nAnalysis complete! Results saved to {output_csv}")
    print(f"Added {len(new_results)} new word entries to {len(existing_data)} existing entries")

if __name__ == "__main__":
    main()