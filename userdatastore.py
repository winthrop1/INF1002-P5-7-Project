import os
from datetime import datetime

def storeDatainTxt(classification, keywords,total_score, EmailDomainMsg, email_text, url_reason_pairs, number_of_urls):
    folder_path = "dataset/safe_keep" # Define the folder name
    os.makedirs(folder_path, exist_ok=True) # Ensure folder exists

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # Generate timestamp for unique file names in the format YYYYMMDD_HHMMSS
    file_name = f"EmailData_{timestamp}.txt" # Create a unique file name using the timestamp
    file_path = os.path.join(folder_path, file_name) # Full path to the file

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("----- Email Analysis Result -----\n\n")
            file.write(f"Classification: {classification}\n")



            if keywords:
                file.write("Keywords Found:\n")
                for kw in keywords:
                    file.write(f"  - {kw}\n")
                file.write("\n")
            else:
                file.write("Keywords Found: None\n\n")
            file.write(f"Total Score: {total_score}\n")
            file.write(f"Email Domain Message: {EmailDomainMsg}\n")
            file.write("="*40 + "\n")
            file.write("\n--- Email Text ---\n")
            file.write(email_text)

        storing_notify = f"Email data stored in {file_path}"
        return storing_notify, True
    
    except Exception as e:
        storing_notify = f"Error storing email data: {e}"
        return storing_notify, False