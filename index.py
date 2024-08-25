from flask import Flask,request,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped,MappedColumn
from flask_mail import Mail,Message
import datetime
import json

with open('config.json','r') as c:
    params = json.load(c) ['params']

app = Flask(__name__)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app.config["SQLALCHEMY_DATABASE_URI"] = params["local_server_url"]

db.init_app(app)

app.config.update(
    MAIL_SERVER ="smtp.gmail.com",
    MAIL_PORT   = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params["email_user"],
    MAIL_PASSWORD = params["email_password"]
)
mail = Mail(app)


class article(db.Model):
    id: Mapped[int] = MappedColumn(primary_key=True)
    title:Mapped[str] = MappedColumn(unique=True,nullable=False)
    content:Mapped[str] = MappedColumn(nullable=False)
    author : Mapped[str] = MappedColumn(nullable=False)
    date : Mapped[datetime.datetime] = MappedColumn(nullable=False)

class Contact(db.Model):
    sno:Mapped[int] = MappedColumn(primary_key=True,autoincrement = True)
    name:Mapped[str] = MappedColumn(nullable=False)
    email:Mapped[str] = MappedColumn(nullable=False)
    msg:Mapped[str] = MappedColumn(nullable=False)
    date:Mapped[datetime.datetime] = MappedColumn(nullable=False)
    location : Mapped[str] = MappedColumn(nullable=False)
    subject  : Mapped[str] = MappedColumn(nullable=False)
    phno : Mapped[str] = MappedColumn(nullable=False)

@app.route('/',methods=["GET"])
def home():
    return render_template('home.html',params="Home")

@app.route('/contact',methods=["GET","POST"])
def contact():
    if (request.method=="POST"):
       namee     = request.form.get("name")
       emaill    = request.form.get("email")
       message      = request.form.get("msg")
       locationn = request.form.get("location")
       sub  = request.form.get("subject")
       number = request.form.get("phno")

       entry = Contact(name=namee,email=emaill,msg=message,location=locationn,subject=sub,phno=number)
       db.session.add(entry)
       db.session.commit()
       msg= Message(
            subject="Message from the blog",
            sender= (namee,emaill),
            recipients=[params["email_user"]],
            body = locationn+'\n'+sub+'\n'+number +'\n'+message 
       )
       mail.send(msg)
    return render_template('contact.html',params="Contact Us") 


app.run(port=5000,debug=True)