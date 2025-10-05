#libraies needed for web scarpping
import csv
import requests #fetching webpage
from lxml import html # used to parse and extract data from html
#import csv #write data to csv file
import os #work with folders in file systems
from dotenv import load_dotenv #for loading environment variables

#load environment variables from .env file
load_dotenv()

#output location
#construct absolute path from environment variable or default
output_folder = os.path.join(os.path.dirname(__file__), os.getenv('OUTPUT_FOLDER', 'keywords/raw_data'))

#check that output is correct so can write files in
if not os.path.exists(output_folder):
    print(f"Location not found: {output_folder}")
    exit(1)

#url of the website we using for spam words
source_url = os.getenv('SPAM_SOURCE_URL', 'https://www.activecampaign.com/blog/spam-words')

#will scarp the words from the website into a list
def get_spam_words():
    resp = requests.get(source_url)
    resp.raise_for_status() #checks status will stop if something is wrong

    doc = html.fromstring(resp.content) #parse html contents using lxml
    
    spam_words = [] #empty list to hold the spam words
    
    #go through ordered list
    ol_elements = doc.xpath('//ol') #// indicated to search all in the doc and ol is to check ordered list

    for ol in ol_elements:
        #go through each list inside each ol
        li_elements = ol.xpath('./li/text()') #. means to check from current which is ol, li is for inside the ol and text() is to get text from inside li
        
        for text in li_elements:
            clean_text = text.strip()
            if clean_text:
                word_count = len(clean_text.split()) #count words in text
                if word_count <= 5:  #only extacting shorts words dont want long sentence
                    spam_words.append(clean_text)
    
    return spam_words  #get list of spam words

# def save_txt(words, filename): #save to txt file
#     #saving the words to the txt file
#     #one word each line
#     with open(filename, "w", encoding="utf-8") as file: 
#         for word in words:
#             file.write(word + "\n")

def save_csv(words, filename): #save to csv file
    #saving the words to the csv file
    #all in 1 column with header spam_word
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["spam_words"]) #column header name
        for word in words:
            writer.writerow([word.lower()])

def main():
    words = get_spam_words()
    #remove the last 3 words
    words = words[:-3]
    print(f"Found {len(words)} spam words.")

    #output paths
    # txt_path = os.path.join(output_folder, "spam_words.txt")
    csv_path = os.path.join(output_folder, "spam_words.csv")

    # save_txt(words, txt_path)
    save_csv(words, csv_path)

if __name__ == "__main__":
    main()