from flask import Flask, request, render_template #import flask and needed modules
from detector import classify_email #import from detector.py
import os #work with folders in file systems
from dotenv import load_dotenv #for loading environment variables

#load environment variables from .env file
load_dotenv()

#initialize flask app
app = Flask(__name__, template_folder=os.getenv('TEMPLATE_FOLDER', 'website')) #create flask app and link to where my html file is

@app.route('/', methods=['GET', 'POST']) #accepts both get and post
def upload_file():
    #variables to hold results 
    classification = None
    EmailDomainMsg = None
    keywords = [] 
    total_score = 0 
    email_text = ''  
    
    if request.method == 'POST': #handle submissions
        file = request.files.get('emailfile')
        if not file: 
            classification = ("Please upload a valid email file.")
        else:
            email_text = file.read().decode('utf-8', errors='ignore') #use utf-8 to read and decode, ignore decoding errors
            classification, keywords, total_score, EmailDomainMsg = classify_email(email_text) #returns the 3

    return render_template("index.html", 
                           classification=classification, #classification
                           keywords=keywords, #keywords found
                           total_score=total_score, #risk score
                           email_content=email_text,
                           EmailDomainMsg=EmailDomainMsg)  #email contents in containers

if __name__ == "__main__": #run website
    app.run(debug=True)