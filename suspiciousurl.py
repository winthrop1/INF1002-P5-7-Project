import validators
from urllib.parse import urlparse
import socket
import whois
import time
from datetime import datetime
import re
import os 
from dotenv import load_dotenv

#url = input("Enter URL to be verified: ")
suspicion_score = 0
reasons = []

file_path = r"C:\Users\User\Documents\GitHub\INF1002-P5-7-Project\spam\spam_1.txt"  # Replace with your file's path


def get_urls_from_email_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            email_content = f.read()
            
            # More comprehensive URL pattern
            url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%]*'
            urls = re.findall(url_pattern, email_content)
            
            print(f"Found {len(urls)} URLs in the file.")
            return urls
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return []

extracted_urls = get_urls_from_email_file(file_path)

if extracted_urls:
    print("Extracted URLs:")
    for i, url in enumerate(extracted_urls, 1):
        print(f"{i}. {url}")
else:
    print("No URLs found or file could not be read.")
    


def domain_resolved(url): # first level check
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc  # This gets the hostname (domain) part of the URL
        
    print(hostname)
    print(len(hostname))
    
    if validators.domain(hostname):
        print(f'Valid domain: {hostname}') #domain is well formatted
    
        try:
            socket.gethostbyname(hostname)
            print(f'Domain {hostname} resolves successfully.')
            return True
        
        except socket.gaierror:
            print(f'Domain {hostname} could not be resolved.')
            return False
        
    else:
        print(f'Invalid domain: {hostname}') #domain is not well formatted
        return False
    
    
#domain_resolved(url)


def check_domain_reputation(url, max_retries = 3, delay = 2): # check domain reputation using WHOIS data
    
    global suspicion_score
    
    today = datetime.now()
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc  # This gets the hostname (domain) part of the URL
        
    
    print(f"Analyzing domain: {hostname}")
    
    
    for attempt in range(max_retries): # Retry mechanism for WHOIS lookup
        try:
            domain_info = whois.whois(hostname)
            break  # Exit the loop if successful
        
        except Exception as e:
            print(f"WHOIS lookup failed on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries:
                time.sleep(delay * attempt)  # Wait before retrying
            else:
                return {"risk": "high", "reason": f"WHOIS lookup failed after {max_retries} attempts: {e}"}

    if domain_info:

        creation_date = domain_info.creation_date # 1. Check Creation Date - New domains are often suspicious
        expiration_date = domain_info.expiration_date
        updated_date = domain_info.updated_date
    
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
    
        if creation_date:
            age_days = (datetime.now() - creation_date).days # Calculate domain age in days

            print(f"Domain age: {age_days} days")
        
            if age_days < 30:
                suspicion_score += 3
                reasons.append("Domain is very new (less than 30 days old), which is often a sign of a suspicious domain.")
            
            
            elif age_days < 121:
                suspicion_score += 2
                reasons.append("Domain is relatively new (between 30 and 120 days old), which can be a sign of a suspicious domain.")
            
        
            elif age_days < 366:
                suspicion_score += 1
                reasons.append("Domain is somewhat new (between 120 and 365 days old), which may warrant caution.")
            
        
            else:
                print("Domain age is good") 
            
        
        print(f'age domain {suspicion_score}')
        
        expiration_date = domain_info.expiration_date # 2. Check Expiration Date - Domains expiring soon can be suspicious
    
    
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        
        if expiration_date:
        
            number_of_days = (expiration_date - today).days
            print(f"Domain expiration in: {number_of_days} days")
        
            if number_of_days < 365:
                suspicion_score += 1
                reasons.append("Domain is set to expire within the next year, as hackers will usually only renew a phishing domain for a year.") 

                print(f'expiration domain {suspicion_score}')

            elif number_of_days < 180:
                suspicion_score += 2
                reasons.append("Domain is set to expire within the next 6 months, which is a sign of suspicious activity.")

                print(f'expiration domain {suspicion_score}')
            
            else:
                print("Domain expiration date is good")
            
        
        else:
            print("No expiration date found")
        
        
        if updated_date and isinstance(updated_date, list): # 3. Check Last Updated Date - Recently updated domains can be suspicious
            updated_date = updated_date[0]
            days_since_update = (today - updated_date).days
            days_since_update_to_expiry = (expiration_date - updated_date).days

            print(f"Domain last updated: {days_since_update} days ago")
            print(f"Days between last update and expiration: {days_since_update_to_expiry} days")
        
            if days_since_update_to_expiry <= 365:
                suspicion_score += 1
                reasons.append(f'Domain was updated {days_since_update} days ago, which is suspicious given its expiration date, {expiration_date}, only extending their lifespan by {days_since_update_to_expiry} days.')

                print(f'updated domain {suspicion_score}')

        else:
            print("No updated date found")


    else:
        print("No WHOIS data found")
            


def having_ip_address(url):
    global suspicion_score
    print("test having ip address")
    match = re.search( # search for digits and dots, with a slash at the end
        '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4
        '((0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\/)' # IPv4 in hexadecimal
        '(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}', url)  # Ipv6
    
    if match:
        suspicion_score += 2
        reasons.append("URL contains an IP address instead of a domain name, which is often used in malicious URLs to obscure the destination")
        
    else:
        reasons.append("URL does not contain an IP address, but proceed with caution")


def https_check(url):
    global suspicion_score
    print("test https")
    if not url.startswith("https://"):
        suspicion_score += 2
        reasons.append("URL does not use HTTPS, which is a strong indicator of insecurity")
        return 
    else:
        print("URL uses HTTPS, which is good")
        return
    
def url_check (url):
    global suspicion_score
    print("test url length")
    
    if len(url) > 75:
        suspicion_score += 1
        reasons.append(f"URL length is unusually long, ({len(url)} characters)")
    else:
        print("URL length is normal")
        reasons.append(f"URL length is normal, ({len(url)} characters), but proceed with caution")   
        
    if '@' in url:
        suspicion_score += 2
        reasons.append("URL contains '@' symbol, which can be used to obscure the real destination")
        
    else:
        print("No '@' symbol found in URL.")
        reasons.append("URL does not contain '@' symbol, but proceed with caution")

    
    
def subdir_count(url):
    global suspicion_score
    parsed_url = urlparse(url)
    #path = parsed_url.lower()
    subdir_count = parsed_url.count('/')  # Count non-empty segments
    
    print("test subdir count")
    
    if subdir_count > 4:
        suspicion_score += 1
        reasons.append(f"URL has a suspiciously high number of subdirectories, ({subdir_count} subdirectories)")
    else:
        reasons.append(f"URL has a normal number of subdirectories, ({subdir_count} subdirectories), but proceed with caution")


def calling_all_functions(url):
    check_domain_reputation(url, max_retries = 3, delay = 2)
    having_ip_address(url)
    https_check(url)
    url_check(url)
    subdir_count(url)
    

def assessing_risk_scores(url):
    global suspicion_score
    
    if domain_resolved(url):
        calling_all_functions(url)
        
    else:
        suspicion_score += 3
        reasons.append("Domain could not be resolved, which is a strong indicator of a suspicious URL")
    
    #def normalize_date(date_value):
            #if date_value and isinstance(date_value, list):
                #return date_value[0]
            #return date_value
    
    if suspicion_score >= 5:
        risk_level = "HIGH"
    elif suspicion_score >= 3:
        risk_level = "MEDIUM"
    elif suspicion_score >= 1:
        risk_level = "LOW"
    else:
        risk_level = "VERY_LOW"
        
    print("testing reasons")

    print(f'Risk Level: {risk_level}')
    print(f'Suspicion Score: {suspicion_score}')
    print("Reasons for suspicion:")
    for reason in reasons:
        print(f'- {reason}') 
    print(f'URL Length: {len(url)} characters')
    print(f'Subdirectory Count: {subdir_count(url)}')
    
    return {
        'risk_level': risk_level,
        'suspicion_score': suspicion_score,
        'reasons': reasons,
        'url_length': len(url),
        'subdirectory_count': subdir_count,
        }
    
#assessing_risk_scores(extracted_urls)