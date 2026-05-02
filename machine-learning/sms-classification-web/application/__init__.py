from flask import Flask, render_template # install package
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)  # magic variable
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///message_classifier.db'
db  = SQLAlchemy(app)

# db.init_app(app)
migrate = Migrate(app, db)

from application import routes



# class Status(enum.Enum):
#     notSpam = 'NOT SPAM'
#     spam = 'SPAM'
    
# class Message(db.Model):
#     id          = db.Column(db.Integer(), primary_key=True)
#     text        = db.Column(db.Text(), nullable = False)
#     statusName = db.Column(db.String(length = 10), nullable=False)
    
#     def __repr__(self):
#         return f'Message {self.text}'



# @app.route("/")  # decorator python
# @app.route("/home")
# def home():
#     return render_template('home.html')

# @app.route("/result")
# def result():
#     messages = Message.query.all()
#     return render_template('result.html', messages=messages)


