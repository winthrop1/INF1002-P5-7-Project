import os
from dotenv import load_dotenv
from datas import unique_from_emails

load_dotenv()  # Load environment variables from .env file
def distance_check(domain1, domain2):
    if len(domain1) < len(domain2):
        return distance_check(domain2, domain1)  # Ensure domain1 is the longer one

    if len(domain2) == 0:
        return len(domain1)  # Early exit if length difference is greater than 1

    previous_row = range(len(domain2) + 1)# Initialize the previous row of distances
    for i, c1 in enumerate(domain1): # Iterate through each character in domain1
        current_row = [i + 1] # Initialize the current row of distances
        for j, c2 in enumerate(domain2): # Iterate through each character in domain2
            insertions = previous_row[j + 1] + 1 # Calculate insertions
            deletions = current_row[j] + 1 # Calculate deletions
            substitutions = previous_row[j] + (c1 != c2) # Calculate substitutions
            current_row.append(min(insertions, deletions, substitutions)) # Append the minimum cost to the current row
        previous_row = current_row # Move to the next row

    return previous_row[-1] # Return the final distance value

def email_titlecheck(email_title):
    text = email_title.lower().strip()
    
    # Case 1: email inside < >
    if '<' in text and '>' in text:
        email = text[text.find('<') + 1:text.find('>', text.find('<') + 1)].strip()
        if '@' in email:
            return email

    # Case 2: fallback (no brackets, find @ manually)
    words = text.replace('(', '').replace(')', '').replace('"', '').split() # split by whitespace
    for w in words:
        if '@' in w and '.' in w:  # basic email pattern
            return w.strip('.,;:><"\' ') # strip common punctuation



def domaincheck(email_title, safe_domains=unique_from_emails, threshold=int(os.getenv("DOMAIN_SIMILARITY_THRESHOLD", "4"))):
    domain_suspicion_score = 0
    email = email_titlecheck(email_title) 
    domain = "@" + email.split('@', 1)[1]
    if domain in safe_domains: #check if domain is in predefined safe list
        EmailDomainMsg = f"{email} is a safe domain. "
        DistanceCheckMsg = "No similar domains found."
        return EmailDomainMsg, DistanceCheckMsg, domain_suspicion_score
    else:
        EmailDomainMsg = f"Warning: {email} is from an unrecognized domain.\n"
        DistanceCheckMsg = "No similar domains found."
        domain_suspicion_score += int(os.getenv("SENDER_KEYWORD_SCORE", "2")) #increase risk score for unrecognized domain
        for safe_domain in safe_domains:
            dist = distance_check(domain, safe_domain)
            if dist <= threshold:
                DistanceCheckMsg = f"Warning: Email domain '{domain}' is similar to a safe domain '{safe_domain}' (with only {dist} change(s) different)\n"
                domain_suspicion_score += dist # increase risk score for similar domain
            elif dist == 0:
                DistanceCheckMsg = 'No similar domains found.'
        return EmailDomainMsg, DistanceCheckMsg, domain_suspicion_score
    
