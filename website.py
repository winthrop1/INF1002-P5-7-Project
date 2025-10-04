from flask import Flask, request, render_template #import flask and needed modules
from email_manage import parse_email_file #import from detector.py
from domainchecker import domaincheck
from suspiciouswords import classify_email
from suspiciousurl import assessing_risk_scores, get_urls_from_email_file
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

@app.route('/', methods=['GET', 'POST']) #accepts both get and post
def upload_file():
    #variables to hold results
    reasons = []
    classification = None
    EmailDomainMsg = ''
    emailnotify = ''
    keywords = []
    total_score = 0
    email_text = ''
    email_title = ''
    email_subject = ''
    email_body = ''

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
            classification, keywords, total_score = classify_email(email_subject, email_body)

            # Domain check
            EmailDomainMsg = domaincheck(email_title)


            risk_level, suspicion_score, reasons = assessing_risk_scores(email_body)

            

            # Send email report to user
            if useremail:
                admin_email = "gachacentral1@gmail.com"

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
                    server.login(admin_email, 'dexksasuvacscfwv') #app password
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
                           EmailDomainMsg=EmailDomainMsg,
                           reasons=reasons, #url analysis reasons
                           emailnotify=emailnotify) #domain check message

if __name__ == "__main__": #run website
    app.run(debug=True)