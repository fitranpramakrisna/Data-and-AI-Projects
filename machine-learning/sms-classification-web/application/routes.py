from json import load
from msilib import text
from application import app
from application import db
from flask import render_template, request, redirect
from application.models import Message
from jcopml.utils import load_model
from sqlalchemy.sql.expression import desc
import logging

# import nltk
# nltk.download('punkt')


model = load_model("dataset/model1.pkl")

@app.route("/")  # decorator python
@app.route("/home")
def home():
    textMessage = 0
    status = 0
    return render_template('home.html', status=status, text = textMessage)


@app.route("/result")
def result():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    messages = Message.query.all()
    
    if messages == []:
        messages = 0
    else:
         page = request.args.get('page', 1, type=int)
         messages  = Message.query.order_by(Message.id.desc()).paginate(page=page, per_page=per_page)
        
    return render_template('result.html', messages=messages, page=page, perpage=per_page)


@app.route("/",methods=['POST'])
def main_page():
    if request.method=='POST':
        textMessage = request.form['text']
        predictingMessage = [textMessage]
        predictingMessage = model.predict(predictingMessage)
        statusMessage = predictingMessage[0]
        
        if statusMessage == 1:
            status = 'SPAM'
        else :
            status = 'NOT SPAM'
            
        newMessage = Message(text = textMessage, statusName=status)
        
        try:
            db.session.add(newMessage)
            db.session.commit()
            return render_template('home.html', status=status, text=textMessage)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return "there's an issue here!"
    else:
        status = 0
        textMessage = 0
        return render_template('home.html', status = status, text = textMessage)
