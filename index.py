from flask import Flask,request,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped,MappedColumn
import datetime

app = Flask(__name__)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@localhost/pythonblog"

db.init_app(app)

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

@app.route('/home',methods=["GET"])
def home():
    return render_template('home.html')

@app.route('/contact',methods=["GET","POST"])
def contact():
    if (request.method=="POST"):
       namee     = request.form.get("name")
       mail    = request.form.get("email")
       message      = request.form.get("msg")
       locationn = request.form.get("location")
       sub  = request.form.get("subject")
       number = request.form.get("phno")

       entry = Contact(name=namee,email=mail,msg=message,location=locationn,subject=sub,phno=number)
       db.session.add(entry)
       db.session.commit()
       

    return render_template('contact.html') 
app.run(port=5000,debug=True)