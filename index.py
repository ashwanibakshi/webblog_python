from flask import Flask,request,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped,MappedColumn
from flask_mail import Mail,Message
from flask_bcrypt import Bcrypt
import datetime
import json



with open('.\config\config.json','r') as c:
    params = json.load(c) ['params']

app = Flask(__name__)
bcrypt = Bcrypt(app)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app.config["SQLALCHEMY_DATABASE_URI"] = params["local_server_url"]

db.init_app(app)

app.config.update(
    MAIL_SERVER   ="smtp.gmail.com",
    MAIL_PORT     = 465,
    MAIL_USE_SSL  = True,
    MAIL_USERNAME = params["email_user"],
    MAIL_PASSWORD = params["email_password"]
)
mail = Mail(app)


class Article(db.Model):
    id: Mapped[int]      = MappedColumn(primary_key=True)
    title: Mapped[str]   = MappedColumn(unique=True,nullable=False)
    content: Mapped[str] = MappedColumn(nullable=False)
    author : Mapped[str] = MappedColumn(nullable=False)
    slug: Mapped[str]    = MappedColumn(nullable=False)
    date : Mapped[datetime.datetime] = MappedColumn(nullable=False)

class Contact(db.Model):
    sno: Mapped[int]        = MappedColumn(primary_key=True,autoincrement = True)
    name: Mapped[str]       = MappedColumn(nullable=False)
    email: Mapped[str]      = MappedColumn(nullable=False)
    msg: Mapped[str]        = MappedColumn(nullable=False)
    location: Mapped[str]   = MappedColumn(nullable=False)
    subject: Mapped[str]    = MappedColumn(nullable=False)
    phno : Mapped[str]      = MappedColumn(nullable=False)
    date:Mapped[datetime.datetime] = MappedColumn(nullable=False)

@app.route('/',methods=["GET"])
def home():
    articles = Article.query.filter() [0:5]
    return render_template('home.html',params="Home",posts=articles)

@app.route('/blog/<slug>',methods=["GET"])
def blog(slug):
    article = Article.query.filter_by(slug=slug).first()
    return render_template('blog.html',params=slug,post=article)

@app.route('/contact',methods=["GET","POST"])
def contact():
    if (request.method=="POST"):
       contact = Contact(
       name     = request.form.get("name"),
       email    = request.form.get("email"),
       msg      = request.form.get("msg"),
       location = request.form.get("location"),
       subject  = request.form.get("subject"),
       phno     = request.form.get("phno")
       )
    #    entry = Contact(name=namee,email=emaill,msg=message,location=locationn,subject=sub,phno=number)
       db.session.add(contact)
       db.session.commit()
       msg= Message(
            subject="Message from the blog",
            sender= (contact.name,contact.email),
            recipients=[params["email_user"]],
            body = contact.location+'\n'+contact.subject+'\n'+contact.phno+'\n'+contact.msg 
       )
       mail.send(msg)
    return render_template('contact.html',params="Contact Us") 

@app.route('/login',methods=["GET","POST"])
def login():
    return render_template('login.html')

@app.route('/register',methods=["GET","POST"])
def register():
    if(request.method=="POST"):
      password = request.form.get("password")
      pwd = bcrypt.generate_password_hash(password)
    return render_template('register.html')

app.run(port=5000,debug=True)