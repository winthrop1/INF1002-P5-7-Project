from flask import Flask, request, render_template, redirect, url_for, session, jsonify  #import flask and needed modules
from email_manage import parse_email_file #import from detector.py
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
app = Flask(__name__, template_folder=os.getenv('TEMPLATE_FOLDER', 'website')) #create flask app and link to where my html file is
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  #add to your .env file

#admin credentials
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin1@gmail.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')


@app.route('/', methods=['GET', 'POST']) #accepts both get and post
def upload_file():
    #variables to hold results
    reasons = []
    classification = None
    EmailDomainMsg = ''
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

            # Classify the email using the original detection system
            classification, keywords, keywords_suspicion_score = classify_email(email_subject, email_body)

            # Domain check
            EmailDomainMsg, domain_suspicion_score = domaincheck(email_title)

            reasons, url_suspicion_score = assessing_risk_scores(email_body)
                        
            total_risk_scoring = keywords_suspicion_score + domain_suspicion_score + url_suspicion_score
                
            if total_risk_scoring >= 9:
                risk_level = "VERY HIGH"
                    
            elif total_risk_scoring >= 7: 
                risk_level = "HIGH"
                    
            elif total_risk_scoring >= 5:
                risk_level = "MEDIUM"
                    
            elif total_risk_scoring >= 3:
                risk_level = "LOW"
                    
            else:
                risk_level = "VERY_LOW"
                    

            # risk_level, suspicion_score, reasons = assessing_risk_scores(email_body)
            
            if "safe" in EmailDomainMsg.lower() and total_risk_scoring >2:
                EmailDomainMsg += "However, potential phishing is detected!"
            

            storing_notify, success = storeDatainTxt(classification, keywords,total_risk_scoring, EmailDomainMsg, email_text)

            # Send email report to user
            if useremail:
                admin_email = os.getenv('EMAIL_ADDRESS')
                admin_key = os.getenv('EMAIL_KEY')

                report_body = (
                    "----- Email Analysis Result -----\n\n"
                    f"Classification: {classification}\n\n"
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
                        EmailDomainMsg=EmailDomainMsg, #domain check message
                        reasons=reasons, #url analysis reasons
                        risk_level=risk_level,#risk scoring of the whole email
                        total_risk_scoring=total_risk_scoring,
                        emailnotify=emailnotify, #email sending notification
                        storing_notify = storing_notify,#data storage notification
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

if __name__ == "__main__": #run website
    app.run(debug=True)