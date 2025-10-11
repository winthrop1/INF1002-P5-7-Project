import validators
from urllib.parse import urlparse
import socket
import whois
import time
from datetime import datetime
import re
import os 
from functools import lru_cache
from itertools import islice
from dotenv import load_dotenv



load_dotenv()
url_suspicion_score = 0
reasons = []


def get_domain_from_url(url): # Extract domain from URL
    try:
        parsed_url = urlparse(url)
        hostnames = parsed_url.netloc
        return hostnames
    except Exception as e:
        print(f"Error extracting domain from {url}: {str(e)}")
        return url.lower()
    

def domain_resolved(url): # first level check
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc  # This gets the hostname (domain) part of the URL
    
    if validators.domain(hostname): #domain is well formatted
    
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
    
    
def retry_whois_lookup(hostname, max_retries=3, delay=1): # Retry WHOIS lookup with exponential backoff
    for attempt in range(max_retries):
        try:
            domain_info = whois.whois(hostname) # Perform WHOIS lookup
            return domain_info # Return the WHOIS data if successful
            
        except Exception as e:
            print(f"WHOIS lookup failed on attempt {attempt + 1}: {e}")
            
            # If this is the last attempt, don't sleep
            if attempt == max_retries - 1:
                print(f"WHOIS lookup failed for {hostname} after {max_retries} attempts")
                return None
            
            # Exponential backoff with jitter to avoid thundering herd
            sleep_time = delay * (2 ** attempt)  # Exponential backoff
            print(f"Retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
    
    return None


@lru_cache(maxsize=1000)
def cached_whois_lookup(hostname): # Cache WHOIS lookups to improve performance
    try:
        return whois.whois(hostname)
    except Exception as e:
        return None
    
def make_comparable(date_time): # Helper function to handle different date formats and convert to naive datetime
    if date_time is None:
        return None
    if isinstance(date_time, list):
        date_time = date_time[0]
    if hasattr(date_time, 'tzinfo') and date_time.tzinfo is not None: # If datetime is aware, convert to naive by removing timezone info
        return date_time.replace(tzinfo=None)
    return date_time
        
def analyze_domain_info(domain_info, hostname):
    
    global url_suspicion_score
    today = datetime.now() 
    
    creation_date = domain_info.creation_date # 1. Check Creation Date - New domains are often suspicious
    expiration_date = domain_info.expiration_date # 2. Check Expiration Date - Domains expiring soon can be suspicious
    updated_date = domain_info.updated_date # 3. Check Last Updated Date - Recently updated domains can be suspicious

    # Normalize dates to naive datetime objects for comparison
    creation_date = make_comparable(creation_date) 
    expiration_date = make_comparable(expiration_date)
    updated_date = make_comparable(updated_date)

    if creation_date: # Check Creation Date - New domains are often suspicious

        try:
            age_days = (today - creation_date).days # Calculate domain age in days
        
            if age_days < 30:
                url_suspicion_score += int(os.getenv("HIGH_DOMAIN_SCORE", "3"))  # increase risk score for very new domains
                reasons.append(f'Domain {hostname} is very new, created on {creation_date}, {age_days} day(s) old, which is often a sign of a suspicious domain.')
            
            elif age_days < 121:
                url_suspicion_score += int(os.getenv("MEDIUM_DOMAIN_SCORE", "2"))  # increase risk score for moderately new domains
                reasons.append(f'Domain {hostname} is relatively new, created on {creation_date}, {age_days} day(s) old, which can be a sign of a suspicious domain.')
            
            elif age_days < 366:
                url_suspicion_score += int(os.getenv("LOW_DOMAIN_SCORE", "1"))  # slight increase in risk score for somewhat new domains
                reasons.append(f'Domain {hostname} is somewhat new, created on {creation_date}, {age_days} day(s) old, which may warrant caution.')
            
            else:
                reasons.append(f'Domain {hostname} is older than a year, created on {creation_date}, {age_days} day(s) old, which is generally a good sign.')
                print("Domain age is good") 
        

        except Exception as e: # Handle potential errors in date calculation
            print(f"Error calculating domain age: {e}")

    
    if expiration_date: # Check Expiration Date - Domains expiring soon can be suspicious

        try:
            number_of_days = (expiration_date - today).days # Calculate days until expiration
        
            if number_of_days < 180:
                url_suspicion_score += int(os.getenv("HIGH_DOMAIN_EXPIRY_SCORE", "2"))  # increase risk score for domains expiring within 6 months
                reasons.append(f"Domain is set to expire on {expiration_date}, in {number_of_days} day(s), which is a sign of suspicious activity.")
            
            elif number_of_days < 365:
                url_suspicion_score += int(os.getenv("LOW_DOMAIN_EXPIRY_SCORE", "1"))  # increase risk score for domains expiring within a year
                reasons.append(f"Domain is set to expire on {expiration_date}, in {number_of_days} day(s). Hackers will usually only purchase or renew a phishing domain for a year.") 
            
            else:
                reasons.append(f"Domain expiration date is {expiration_date}, in {number_of_days} day(s), which is generally a good sign.")
            
        except Exception as e: # Handle potential errors in date calculation
            print(f"Error calculating domain expiration: {e}")

    else:
        print("No expiration date found")
        
    
    if updated_date and expiration_date: #Check Last Updated Date - Recently updated domains can be suspicious
        try:
            days_since_update = (today - updated_date).days # Calculate days since last update
            days_since_update_to_expiry = (expiration_date - updated_date).days # Calculate days between last update and expiration
        
            if days_since_update_to_expiry <= 365: 
                url_suspicion_score += int(os.getenv("DOMAIN_UPDATE_SCORE", "1"))  # increase risk score for recently updated domains with short time to expiry
                reasons.append(f'Domain was updated {days_since_update} day(s) ago, which is suspicious given its expiration date, {expiration_date}, only extending their lifespan by {days_since_update_to_expiry} day(s).')

            else:
                print("No updated date found")

        except Exception as e:
            print(f"Error calculating domain update info: {e}")

    else:
        print("No WHOIS data found")
        
def check_domain_reputation(url):  #check domain reputation using WHOIS data, with a max retry of 3, and a delay of 2 seconds between retries
    
    global url_suspicion_score # Use global variable to track suspicion score
    
    parsed_url = urlparse(url) 
    hostname = parsed_url.netloc  # This gets the hostname (domain) part of the URL
    
    cached_domain_info = cached_whois_lookup(hostname)
    
    if cached_domain_info is None:
        domain_info = retry_whois_lookup(hostname, max_retries = 3, delay = 1) # Retry WHOIS lookup with exponential backoff
    else:
        domain_info = cached_domain_info

    if domain_info: # If WHOIS data is found, analyze it
        analyze_domain_info(domain_info, hostname)
    else:
        print(f"No WHOIS data found for {hostname}")

                


def having_ip_address(url):
    global url_suspicion_score
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc.split(':')[0]  # This gets the hostname (domain) part of the URL, removing port number if present

    ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$' # Regex pattern for IPv4
    ipv6_pattern = r'^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$' # Regex pattern for IPv6
    
    # Check for various obfuscated formats
    obfuscated_formats = [
        (r'^0x[0-9a-fA-F]{1,8}$', 'hexadecimal_ip'), # Hexadecimal IP (0x455e8c6f)
        (r'^\d{8,10}$', 'dword_ip'), # Dword IP (3232235777)
        (r'^0[0-7]{1,3}(\.[0-7]{1,3}){3}$', 'octal_ip'), # Octal IP (0177.0.0.1)
        (r'^(0x[0-9a-fA-F]{1,2}\.){3}0x[0-9a-fA-F]{1,2}$', 'mixed_hex_ip'), # Mixed hex notation (0xC0.0xA8.0x01.0x01)
        (r'^0x[0-9a-fA-F]{8}$', 'combined_hex_ip') # Combined hex (0xC0A80101)
    ]

    standard_ip_address = re.match(ipv4_pattern, hostname) or re.match(ipv6_pattern, hostname, re.IGNORECASE) #check if hostname is an IP address in IPv4 or IPv6 format 
    
    obfuscated_match = None
    for pattern, format_type in obfuscated_formats: #check if hostname matches any obfuscated IP address formats
        if re.match(pattern, hostname, re.IGNORECASE):
            obfuscated_match = format_type #format type found is stored in obfuscated_match 
            break
    
    if standard_ip_address:
        url_suspicion_score += int(os.getenv("IP_ADDRESS_SCORE", "2"))  # increase risk score for URLs with IP addresses
        reasons.append("URL contains an IP address instead of a domain name, which is often used in malicious URLs to obscure the destination")

    elif obfuscated_match:
        url_suspicion_score += int(os.getenv("IP_ADDRESS_SCORE", "2"))  # increase risk score for URLs with obfuscated IP addresses
        reasons.append("URL contains an obfuscated IP address instead of a domain name, which is often used in malicious URLs to obscure the destination")
        
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
    check_domain_reputation(longest_url)
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
        urls_in_email = re.compile(r"https?://[^\s]+") # Regex pattern to match URLs starting with http or https
        urls = [re.split(r'[<>"\'&]', url)[0].rstrip('.,;:') for url in urls_in_email.findall(email_body)] # Clean URLs by removing trailing punctuation and splitting at certain characters
        
        print(f"Found {len(urls)} URLs in the file.")

        number_of_urls = len(urls)
        
        if urls: #if there are URLs in the email

            urls_with_unique_domains = {} #empty dictionary for urls with no repeated domain names
            url_reason_pairs = []

            for url in urls:
                domain = get_domain_from_url(url) #uses the function to extract the domain name. e.g. google.com
                
                #if the domain is not in the dictionary(urls_with_unique_domains), update the dict. If the domain name is already in the dictionary, compare the length of the url and update the dict with the longer url
                if domain not in urls_with_unique_domains or len(url) > len(urls_with_unique_domains[domain]): 
                    urls_with_unique_domains[domain] = url #write the url into the dictionary

            limited_domains = dict(islice(urls_with_unique_domains.items(), 6)) # takes the first 6 items from the dictionary

            number_of_unique_domains = len(urls_with_unique_domains)

            if len(urls_with_unique_domains) > 6: #limit to first 6 domains for performance
                print(f"Limiting processing to first 6 domains out of {len(urls_with_unique_domains)} total domains")
                reasons.append(f"Email contains {len(urls_with_unique_domains)} unique domains. Limited analysis to first 6 domains for performance.")
            else:
                print(f"Processing all {len(urls_with_unique_domains)} unique domains:")

            for domain, longest_url in limited_domains.items(): #go through each domain and its corresponding longest url in the dictionary
            
                url_specific_reasons = []
                
                if domain_resolved(longest_url): #if the domain can be resolved
                    reasons = []
                    calling_all_functions(longest_url) #call all the functions to assess the url
                    url_specific_reasons = reasons.copy()
                    url_reason_pairs.append({ #append the url and its specific reasons to the list
                        'url': longest_url,
                        'reasons': url_specific_reasons.copy()
                    })
                    
                else: #if the domain cannot be resolved
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
        

    return reasons, url_suspicion_score, url_reason_pairs, number_of_urls, number_of_unique_domains