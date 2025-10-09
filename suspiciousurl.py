import validators
from urllib.parse import urlparse
import socket
import whois
import time
from datetime import datetime, timezone
import re
import os 
from dotenv import load_dotenv



load_dotenv()
url_suspicion_score = 0
reasons = []


def get_domain_from_url(url):
    """Extract domain from URL using the same method as check_domain_reputation"""
    try:
        parsed_url = urlparse(url)
        print(f'{parsed_url} this is parsed url')
        hostnames = parsed_url.netloc
        print(f'{hostnames} this is get domain')
        return hostnames
    except Exception as e:
        print(f"Error extracting domain from {url}: {str(e)}")
        return url.lower()
    

def domain_resolved(url): # first level check
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc  # This gets the hostname (domain) part of the URL
        
    print(hostname)
    print(len(hostname))
    
    if validators.domain(hostname):
        print(f'Valid domain: {hostname}') #domain is well formatted
    
        try:
            socket.gethostbyname(hostname) # Try to resolve the domain to an IP address
            print(f'Domain {hostname} resolves successfully.') 
            return True
        
        except socket.gaierror: # Handle domain resolution failure
            print(f'Domain {hostname} could not be resolved.')
            return False
        
    else:
        print(f'Invalid domain: {hostname}') #domain is not well formatted
        return False
    

def check_domain_reputation(url, max_retries = 3, delay = 2):  #check domain reputation using WHOIS data, with a max retry of 3, and a delay of 2 seconds between retries
    
    global url_suspicion_score # Use global variable to track suspicion score
    
    today = datetime.now() 
    parsed_url = urlparse(url) 
    hostname = parsed_url.netloc  # This gets the hostname (domain) part of the URL
        
    
    print(f"Analyzing domain: {hostname}")
    
    domain_info = None

    for attempt in range(max_retries): # Retry mechanism for WHOIS lookup
        try:
            domain_info = whois.whois(hostname) # Perform WHOIS lookup
            break  # Exit the loop if successful
        
        except Exception as e:
            print(f"WHOIS lookup failed on attempt {attempt + 1}: {e}") # Log the error
            
            if attempt < max_retries: # If not the last attempt, wait and retry
                time.sleep(delay * attempt)  # Wait before retrying
            else:
                return {"risk": "high", "reason": f"WHOIS lookup failed after {max_retries} attempts: {e}"}

    if domain_info: # If WHOIS data is found, analyze it

    

        creation_date = domain_info.creation_date # 1. Check Creation Date - New domains are often suspicious
        expiration_date = domain_info.expiration_date # 2. Check Expiration Date - Domains expiring soon can be suspicious
        updated_date = domain_info.updated_date # 3. Check Last Updated Date - Recently updated domains can be suspicious
    

        def make_comparable(dt):
            if dt is None:
                return None
            if isinstance(dt, list):
                dt = dt[0]
            # If datetime is aware, convert to naive by removing timezone info
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt


        # if isinstance(creation_date, list):
        #     creation_date = creation_date[0]

        creation_date = make_comparable(creation_date)
        expiration_date = make_comparable(expiration_date)
        updated_date = make_comparable(updated_date)
    
        if creation_date:

            try:
                age_days = (today - creation_date).days # Calculate domain age in days
            
                if age_days < 30:
                    url_suspicion_score += int(os.getenv("HIGH_DOMAIN_SCORE", "3"))  # increase risk score for very new domains
                    reasons.append("Domain is very new (less than 30 days old), which is often a sign of a suspicious domain.")
                
                
                elif age_days < 121:
                    url_suspicion_score += int(os.getenv("MEDIUM_DOMAIN_SCORE", "2"))  # increase risk score for moderately new domains
                    reasons.append("Domain is relatively new (between 30 and 120 days old), which can be a sign of a suspicious domain.")
                
            
                elif age_days < 366:
                    url_suspicion_score += int(os.getenv("LOW_DOMAIN_SCORE", "1"))  # slight increase in risk score for somewhat new domains
                    reasons.append("Domain is somewhat new (between 120 and 365 days old), which may warrant caution.")
                
            
                else:
                    reasons.append("Domain is older than a year, which is generally a good sign.")
                    print("Domain age is good") 
            
        
                print(f'age domain {url_suspicion_score}')

            except Exception as e:
                print(f"Error calculating domain age: {e}")
                
        
        # expiration_date = domain_info.expiration_date # 2. Check Expiration Date - Domains expiring soon can be suspicious
    
    
        # if isinstance(expiration_date, list): 
        #     expiration_date = expiration_date[0]
        
        if expiration_date:

            try:
        
                number_of_days = (expiration_date - today).days # Calculate days until expiration
                print(f"Domain expiration in: {number_of_days} days")
            
                if number_of_days < 180:
                    url_suspicion_score += int(os.getenv("HIGH_DOMAIN_EXPIRY_SCORE", "2"))  # increase risk score for domains expiring within 6 months
                    reasons.append("Domain is set to expire within the next 6 months, which is a sign of suspicious activity.")

                    print(f'expiration domain {url_suspicion_score}')
                
                elif number_of_days < 365:
                    url_suspicion_score += int(os.getenv("LOW_DOMAIN_EXPIRY_SCORE", "1"))  # increase risk score for domains expiring within a year
                    reasons.append("Domain is set to expire within the next year, as hackers will usually only renew a phishing domain for a year.") 

                    print(f'expiration domain {url_suspicion_score}')
                
                else:
                    print("Domain expiration date is good")
                    print(f'expiration domain {url_suspicion_score}')
                
            
            except Exception as e:
                print(f"Error calculating domain expiration: {e}")

        else:
            print("No expiration date found")
            
        
        if updated_date and expiration_date: # 3. Check Last Updated Date - Recently updated domains can be suspicious
            try:
            #updated_date = updated_date[0] 
                days_since_update = (today - updated_date).days # Calculate days since last update
                days_since_update_to_expiry = (expiration_date - updated_date).days # Calculate days between last update and expiration

                print(f"Domain last updated: {days_since_update} days ago")
                print(f"Days between last update and expiration: {days_since_update_to_expiry} days")
            
                if days_since_update_to_expiry <= 365: 
                    url_suspicion_score += int(os.getenv("DOMAIN_UPDATE_SCORE", "1"))  # increase risk score for recently updated domains with short time to expiry
                    reasons.append(f'Domain was updated {days_since_update} days ago, which is suspicious given its expiration date, {expiration_date}, only extending their lifespan by {days_since_update_to_expiry} days.')

                    print(f'updated domain {url_suspicion_score}')

                else:
                    print("No updated date found")

            except Exception as e:
                print(f"Error calculating domain update info: {e}")


        else:
            print("No WHOIS data found")
                


def having_ip_address(url):
    global url_suspicion_score
    match = re.search( # search for digits and dots, with a slash at the end 
        '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4
        '((0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\/)' # IPv4 in hexadecimal
        '(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}', url)  # Ipv6
    
    if match:
        url_suspicion_score += int(os.getenv("IP_ADDRESS_SCORE", "2"))  # increase risk score for URLs with IP addresses
        reasons.append("URL contains an IP address instead of a domain name, which is often used in malicious URLs to obscure the destination")
        
    else:
        reasons.append("URL does not contain an IP address, but proceed with caution")


def https_check(url):
    global url_suspicion_score

    if url.startswith("http://"):
        reasons.append("URL uses HTTP, information sent between your browser and a website is not encrypted")
        url_suspicion_score += int(os.getenv("HTTP_SCORE", "1"))  # increase risk score for URLs using HTTP instead of HTTPS
        return 
    elif not url.startswith("https://"): # Check if URL starts with https
        url_suspicion_score += int(os.getenv("NO_HTTPS_SCORE", "2"))  # increase risk score for URLs not using HTTPS
        reasons.append("URL does not use HTTPS, which is a strong indicator of insecurity")
        return
    else:
        reasons.append("URL uses HTTPS, which is good")
        return
    
def url_check (url):
    global url_suspicion_score
    
    if len(url) > 75: # Check if URL length is greater than 75 characters
        url_suspicion_score += int(os.getenv("LONG_URL_SCORE", "1"))  # increase risk score for long URLs
        reasons.append(f"URL length is unusually long, ({len(url)} characters)")
    else:
        print("URL length is normal")
        reasons.append(f"URL length is normal, ({len(url)} characters), but proceed with caution")   
        
    if '@' in url: # Check if URL contains '@' symbol
        url_suspicion_score += int(os.getenv("AT_SYMBOL_SCORE", "2"))  # increase risk score for URLs with '@' symbol
        reasons.append("URL contains '@' symbol, which can be used to obscure the real destination")
        
    else:
        print("No '@' symbol found in URL.")
        reasons.append("URL does not contain '@' symbol, but proceed with caution")



def calling_all_functions(longest_url):
    check_domain_reputation(longest_url, max_retries = 3, delay = 2)
    having_ip_address(longest_url)
    https_check(longest_url)
    url_check(longest_url)

    

def assessing_risk_scores(email_body):
    global url_suspicion_score
    global reasons
    
    url_suspicion_score = 0
    reasons = []
    number_of_urls = 0
    number_of_unique_domains = 0
    
    try: 
        url_pattern = re.compile(r"https?://[^\s]+") # Regex pattern to match URLs starting with http or https
        urls = re.findall(url_pattern, email_body) # Find all URLs in the email content
            
        print(f"Found {len(urls)} URLs in the file.")

        number_of_urls = len(urls)
        
        if urls: #if there are URLs in the email
            print("Extracted URLs:")

            urls_with_unique_domains = {} #empty dictionary for urls with no repeated domain names
            url_reason_pairs = []

            for url in urls:
                domain = get_domain_from_url(url) #uses the function to extract the domain name. e.g. google.com
                
                #if the domain is not in the dictionary(urls_with_unique_domains), update the dict. If the domain name is already in the dictionary, compare the length of the url and update the dict with the longer url
                if domain not in urls_with_unique_domains or len(url) > len(urls_with_unique_domains[domain]): 
                    urls_with_unique_domains[domain] = url #write the url into the dictionary

            print(f"Processing {len(urls_with_unique_domains)} unique domains:")

            limited_domains = dict(list(urls_with_unique_domains.items())[:6])

            number_of_unique_domains = len(urls_with_unique_domains)

            if len(urls_with_unique_domains) > 6:
                print(f"Limiting processing to first 6 domains out of {len(urls_with_unique_domains)} total domains")
                reasons.append(f"Email contains {len(urls_with_unique_domains)} unique domains. Limited analysis to first 6 domains for performance.")
            else:
                print(f"Processing all {len(urls_with_unique_domains)} unique domains:")


            for domain, longest_url in limited_domains.items():
                print(f"Domain: {domain}, Longest URL: {longest_url}")
            
                url_specific_reasons = []
                
                if domain_resolved(longest_url):
                    reasons = []
                    calling_all_functions(longest_url)
                    url_specific_reasons = reasons.copy()
                    url_reason_pairs.append({
                        'url': longest_url,
                        'reasons': url_specific_reasons.copy()
                    })
                    
                else:
                    url_suspicion_score += int(os.getenv("UNRESOLVED_DOMAIN_SCORE", "3"))  # increase risk score for domains that cannot be resolved
                    
                    reason_text = f"Domain {domain} could not be resolved, which is a strong indicator of a suspicious URL"
                    reasons.append(reason_text)
                    url_specific_reasons.append(reason_text)
                    
                    url_reason_pairs.append({
                        'url': longest_url,
                        'reasons': url_specific_reasons.copy()
                    })

        else: #if no URLs
            url_reason_pairs = []
            print("No URLs found or file could not be read.") 
            url_suspicion_score += int(os.getenv("NO_URLS_FOUND", "0"))
            no_url_found = "No URLs found in the email."
            reason_text = "The email does not contain any URLs"
            reasons.append(reason_text)
            url_reason_pairs.append({
                'url': no_url_found,
                'reasons': [reason_text]
            })
            
        
    
    
    except Exception as e: # Handle other exceptions
        print(f"An error occurred while reading the file: {e}")
        return [], 0, [], 0, 0
    
    
    if url_suspicion_score >= int(os.getenv("HIGH_URL_RISK_THRESHOLD", "5")):
        risk_level = "HIGH"
    elif url_suspicion_score >= int(os.getenv("MEDIUM_URL_RISK_THRESHOLD", "3")):
        risk_level = "MEDIUM"
    elif url_suspicion_score >= int(os.getenv("LOW_URL_RISK_THRESHOLD", "1")):
        risk_level = "LOW"
    else:
        risk_level = "VERY_LOW"
        
    print("testing reasons")
    print(f'Risk Level: {risk_level}')
    print(f'Suspicion Score: {url_suspicion_score}')
    print("Reasons for suspicion:")
  
    
    
    if urls and len(urls) > 0:
        sample_url = urls[0]  
        print(f'URL Length: {len(sample_url)} characters')
    else:
        print('URL Length: N/A')
        print('Subdirectory Count: N/A')

    return reasons, url_suspicion_score, url_reason_pairs, number_of_urls, number_of_unique_domains