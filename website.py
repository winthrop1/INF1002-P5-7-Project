from flask import Flask, request, render_template, redirect, url_for, session, jsonify  #import flask and needed modules
from email_manage import parse_email_file
from domainchecker import domaincheck
from suspiciouswords import classify_email
from suspiciousurl import assessing_risk_scores#, get_urls_from_email_file
from userdatastore import storeDatainTxt
import os #work with folders in file systems
import smtplib
import socket
from email.message import EmailMessage
from email.utils import parseaddr
from dotenv import load_dotenv #for loading environment variables

#load environment variables from .env file
load_dotenv()

#initialize flask app
# app = Flask(__name__, template_folder=os.getenv('TEMPLATE_FOLDER', 'website')) #create flask app and link to where my html file is
app = Flask(__name__, 
            template_folder=os.getenv('TEMPLATE_FOLDER', 'website'),
            static_folder='website',  # Tells Flask where static files are
            static_url_path='')       # Makes URLs like /css/styles.css work
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  #add to your .env file

#admin credentials
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', '1')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '1')

@app.route('/', methods=['GET', 'POST']) #accepts both get and post
def upload_file():
    #variables to hold results
    reasons = []
    url_reason_pairs = []
    classification = None
    EmailDomainMsg = ''
    DistanceCheckMsg = ''
    emailnotify = ''
    storing_notify = ''
    success = bool
    keywords = []
    total_score = 0
    email_text = ''
    email_title = ''
    email_subject = ''
    email_body = ''
    risk_level = ''
    total_risk_scoring = 0
    number_of_urls = 0
    number_of_unique_domains = 0

    if request.method == 'POST': #handle submissions
        file = request.files.get('emailfile')
        useremail = request.form.get('userEmail')

        if not file:
            classification = ("Please upload a valid email file.")
        else:
            # Read and decode the uploaded file
            email_text = file.read().decode('utf-8', errors='ignore') #use utf-8 to read and decode, ignore decoding errors

            # Parse email using the parse_email_file function
            email_title, email_subject, email_body = parse_email_file(email_text)

            # Domain check
            EmailDomainMsg, DistanceCheckMsg, domain_suspicion_score = domaincheck(email_title)

            # URL analysis
            reasons, url_suspicion_score, url_reason_pairs, number_of_urls, number_of_unique_domains = assessing_risk_scores(email_body)

            # Classify the email using the original detection system
            keywords, keywords_suspicion_score = classify_email(email_subject, email_body)
            
            # Apply component-level caps (prevents any single component from dominating)
            domain_capped = min(domain_suspicion_score, int(os.getenv("MAX_DOMAIN_SCORE", "15")))       # Cap domain at 15
            url_capped = min(url_suspicion_score, int(os.getenv("MAX_URL_SCORE", "6")))            # Cap URLs at 6
            keywords_capped = min(keywords_suspicion_score, int(os.getenv("MAX_KEYWORD_SCORE", "15")))  # Cap keywords at 15

            total_risk_scoring = domain_capped + url_capped + keywords_capped
                
            if total_risk_scoring >= int(os.getenv("VERY_HIGH_RISK_THRESHOLD", "16")):
                risk_level = "VERY HIGH"
            elif total_risk_scoring >= int(os.getenv("HIGH_RISK_THRESHOLD", "12")):
                risk_level = "HIGH"
            elif total_risk_scoring >= int(os.getenv("MEDIUM_RISK_THRESHOLD", "8")):
                risk_level = "MEDIUM"
            elif total_risk_scoring >= int(os.getenv("LOW_RISK_THRESHOLD", "4")):
                risk_level = "LOW"
            else:
                risk_level = "VERY_LOW"

            # risk_level, suspicion_score, reasons = assessing_risk_scores(email_body)
            
            if "safe" in EmailDomainMsg.lower() and total_risk_scoring >int(os.getenv("MEDIUM_RISK_THRESHOLD", "8")):
                EmailDomainMsg += "However, potential phishing is detected!"

            classification = "Safe" if total_risk_scoring <= int(os.getenv("PHISHING_SCORE", "8")) else "Phishing"

            # Store analysis results in a text file
            storing_notify, success = storeDatainTxt(classification, keywords,total_risk_scoring, EmailDomainMsg, email_text, url_reason_pairs, number_of_urls)

            # Send email report to user
            if useremail:
                admin_email = os.getenv('EMAIL_ADDRESS')
                admin_key = os.getenv('EMAIL_KEY')

                report_body = (
                    "----- Email Analysis Result -----\n\n"
                    f"Classification: {classification}\n\n"
                    f"URL Analysis Reasons: {', '.join(f'{d.get('url', 'N/A')}: {d.get('reason', 'N/A')}' for d in url_reason_pairs) if url_reason_pairs else 'None'}\n\n"
                    f"Keywords Found: {', '.join(keywords) if keywords else 'None'}\n\n"
                    f"Total Risk Score: {total_score}\n\n"
                    f"Domain Check Message: {EmailDomainMsg}\n"
                    "Email Content:\n"
                    f"{email_text}\n\n"
                )

                msg = EmailMessage()
                msg['From'] = admin_email
                msg['To'] = useremail
                msg['Subject'] = 'Your Email Phishing Analysis Report'
                msg.set_content(report_body)

                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(admin_email, admin_key) #app password
                    server.send_message(msg)
                    server.quit()
                    emailnotify = "Email sent successfully."
                except (socket.gaierror, smtplib.SMTPException, Exception) as e:
                        emailnotify = f"Failed to send email: {e}"

    return render_template("index.html",
                        classification=classification, #classification
                        keywords=keywords, #keywords found
                        total_score=total_score, #risk score
                        email_content=email_text, #original email content
                        email_title=email_title, #parsed email title
                        email_subject=email_subject, #parsed email subject
                        email_body=email_body, #parsed email body
                        EmailDomainMsg=EmailDomainMsg,#domain check message
                        DistanceCheckMsg=DistanceCheckMsg, #distance check message
                        reasons=reasons, #url analysis reasons
                        risk_level=risk_level,#risk scoring of the whole email
                        total_risk_scoring=total_risk_scoring,
                        emailnotify=emailnotify, #email sending notification
                        storing_notify = storing_notify,#data storage notification
                        url_reason_pairs = url_reason_pairs,#list of what url is being assessed and its reasons
                        number_of_urls = number_of_urls, #number of urls found in the email
                        number_of_unique_domains = number_of_unique_domains, #number of unique domains found in the email
                        success = success)

@app.route('/admin-login-json', methods=['POST'])
def admin_login_json():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Invalid email or password."})


@app.route('/admin')
def admin_page():
    if not session.get('admin_logged_in'):
        return redirect(url_for('upload_file'))
    return render_template("adminPage.html")


@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('upload_file'))


#testing admin dashboard 
import glob
from collections import Counter
import re

def parse_stored_emails():
    """Parse all email data files and extract statistics"""
    safe_count = 0
    phishing_count = 0
    all_keywords = []
    
    #extract all .txt files from safe_keep folder
    folder_path = os.path.join(os.path.dirname(__file__), 'dataset', 'safe_keep', '*.txt')
    files = glob.glob(folder_path)
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                #extract classification
                classification_match = re.search(r'Classification:\s*(Safe|Phishing)', content, re.IGNORECASE)
                if classification_match:
                    classification = classification_match.group(1)
                    if classification.lower() == 'safe':
                        safe_count += 1
                    else:
                        phishing_count += 1
                
                #extract keywords to match your format
                #find all lines with "Suspicious word in..." and extract text between quotes
                keyword_matches = re.findall(r"Suspicious word in (?:subject|remaining body):\s*'([^']+)'", content)
                all_keywords.extend(keyword_matches)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            continue
    
    #count keyword frequencies
    keyword_counter = Counter(all_keywords)
    top_keywords = keyword_counter.most_common(5)
    
    return {
        'safe_count': safe_count,
        'phishing_count': phishing_count,
        'top_keywords': top_keywords,
        'total_emails': safe_count + phishing_count
    }

@app.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint to provide dashboard data"""
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = parse_stored_emails()
    
    return jsonify({
        "safe_count": data['safe_count'],
        "phishing_count": data['phishing_count'],
        "top_keywords": [
            {"keyword": keyword, "count": count} 
            for keyword, count in data['top_keywords']
        ],
        "total_emails": data['total_emails']
    })

if __name__ == "__main__": #run website
    app.run(debug=True)