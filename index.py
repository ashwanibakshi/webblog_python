from flask import Flask,request,render_template,redirect,flash,session, url_for
from flask_mail import Mail,Message
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,login_required, login_user,current_user, logout_user
import json
from models.dbModels import db,Article,Contact,Users



with open('.\config\config.json','r') as c:
    params = json.load(c) ['params']

app = Flask(__name__)
bcrypt = Bcrypt(app)

login_manger = LoginManager()
login_manger.login_view='login'
login_manger.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = params["local_server_url"]

db.init_app(app)

app.config.update(
    MAIL_SERVER   ="smtp.gmail.com",
    MAIL_PORT     = 465,
    MAIL_USE_SSL  = True,
    MAIL_USERNAME = params["email_user"],
    MAIL_PASSWORD = params["email_password"],
    SECRET_KEY    = "Secret@123"
)
mail = Mail(app)

@login_manger.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=int(user_id)).first()

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
    if(request.method=="POST"):
        users = Users.query.filter_by(email=request.form.get("email")).first() 
        if (users is not None):
            pwd  = request.form.get("password")
            if(bcrypt.check_password_hash(users.password,pwd)):
                if(request.form.get('remember') is not None):
                   login_user(users,True)
                else:   
                    login_user(users,False)   
                return redirect('/dashboard')
            else:
              flash('Wrong Email Password','danger')  
        else:
           flash('User Is Not Registered','danger')  
    return render_template('login.html')

@app.route('/register',methods=["GET","POST"])
def register():
    if(request.method=="POST"):
      users = Users.query.filter_by(email=request.form.get('email')).first()
      if (users is not None): 
       flash('User Already Registered','danger')  
      else:
       user = Users(
          name     = request.form.get("name"),
          email    = request.form.get("email"),
          password = bcrypt.generate_password_hash(request.form.get("password"))
       )
       db.session.add(user)
       db.session.commit() 
    return render_template('register.html')

@app.route('/dashboard',methods=["GET"])
@login_required
def dash():
    return render_template('dashboard.html',data=current_user.name)


@app.route('/logout',methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for('login'))

app.run(port=5000,debug=True)