from datas import unique_from_emails

def distance_check(domain1, domain2):
    if len(domain1) < len(domain2):
        return distance_check(domain2, domain1)  # Ensure domain1 is the longer one

    if len(domain2) == 0:
        return len(domain1)  # Early exit if length difference is greater than 1

    previous_row = range(len(domain2) + 1)
    for i, c1 in enumerate(domain1):
        current_row = [i + 1]
        for j, c2 in enumerate(domain2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def domaincheck(email_title, safe_domains=unique_from_emails, threshold=4):
    risk_score = 0
    text = email_title.lower() #convert email text to lowercase
    start = text.find('<') + 1 #find the first character of the email address after <
    end = text.find('>', start) #it looks for > and start means it start looking from the position of start which is the first character of the email address
    email = text[start:end].strip()#extract the text between < and > and remove any leading or trailing whitespace
    domain = "@" + email.split('@', 1)[1]
    if domain in safe_domains: #check if domain is in predefined safe list
        EmailDomainMsg = f"Email is from a safe domain: {email}"
        for safe_domain in safe_domains:
            dist = distance_check(domain, safe_domain)
            if dist <= threshold:
                EmailDomainMsg += f"Warning: Email domain '{domain}' is similar to safe domain '{safe_domain}' (with distance {dist})."
                risk_score += 1*dist  # increase risk score for similar domain
        return EmailDomainMsg, risk_score
    else:
        EmailDomainMsg = f"Warning: Email is from an unrecognized domain: {email}"
        risk_score += 2 #increase risk score for unrecognized domain
        for safe_domain in safe_domains:
            dist = distance_check(domain, safe_domain)
            if dist <= threshold:
                EmailDomainMsg += f"Warning: Email domain '{domain}' is similar to safe domain '{safe_domain}' (with distance {dist})."
                risk_score += 1*dist  # increase risk score for similar domain
        return EmailDomainMsg, risk_score