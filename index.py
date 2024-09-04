import math
from flask import Flask,request,render_template,redirect,flash,session, url_for
from flask_mail import Mail,Message
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,login_required, login_user,current_user, logout_user
import json

from slugify import slugify
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
    articles = Article.query.filter().all()
    
    page = request.args.get('page')
    last = math.ceil(len(articles)/int(params['no_of_posts']))

    if (not str(page).isnumeric()):
      page = 1
      
    page = int(page)  
    articles = articles[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    if page==1:
     prev = "#"
     next = "/?page="+ str(page+1)
    elif page==last:
     prev = "/?page="+ str(page-1)
     next = "#"
    else:
     prev = "/?page="+ str(page-1)
     next = "/?page="+ str(page+1)
    return render_template('home.html',params="Home",posts=articles,prev=prev,next=next)

@app.route('/blog/<slugg>',methods=["GET"])
def blog(slugg):
    article = Article.query.filter_by(slug=slugg).join(Users,Article.authorId==Users.id).add_columns(Users.name,Article.id,Article.title,Article.slug,Article.content,Article.date).first()  
    print(article)
    return render_template('blog.html',params=slugg,post=article)

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
                return redirect('dashboard')
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
    dashData = Article.query.filter_by(authorId=current_user.id).all()
    print(dashData)
    return render_template('/dashboard/dashboard.html',blogs=dashData,params="DashBoard",aid=current_user.id)

@app.route('/addpost',methods=["GET","POST"])
@login_required
def addpost():
    if(request.method=="POST"):
        article = Article(
           title    = request.form.get("title"),
           slug     = slugify(request.form.get("slug")),
           content  = request.form.get("content"),
           authorId = request.form.get("authorId")
        )
        db.session.add(article)
        db.session.commit()
    return render_template('/dashboard/addpost.html',author=current_user.name, authorId=current_user.id,params="Add Post",aid=current_user.id)


@app.route('/editpost',methods=["POST"])
@login_required
def editPost():
     uid = request.form.get("authorid")
     id  = request.form.get("blogid")
     postData = Article.query.filter_by(id=id,authorId=uid).first() 
     return render_template('/dashboard/editpost.html',data=postData,params="Edit Post",aid=current_user.id)

@app.route('/updatepost',methods=["POST"])
@login_required
def updatePost():
    editData = Article.query.filter_by(id=request.form.get("id"),authorId=request.form.get("authorid")).first()
    editData.title   = request.form.get("title")
    editData.slug    = request.form.get("slug")
    editData.content = request.form.get("content")
    db.session.commit()
    return redirect('/dashboard')

@app.route('/deletepost',methods=["POST"])
@login_required
def delete():
   Article.query.filter_by(id=request.form.get('blogid'),authorId=request.form.get("authorid")).delete()
   db.session.commit()
   return redirect('/dashboard')


@app.route('/profile/<aid>',methods=["GET"])
@login_required
def profile(aid):
   uData = Users.query.filter_by(id=aid).first()
   return render_template('/dashboard/profile.html',data=uData)

@app.route('/profile',methods=["POST"])
@login_required
def profilee():
    uData = Users.query.filter_by(id=request.form.get("authorid")).first()
    uData.email = request.form.get("email")
    uData.name  = request.form.get("name")

    db.session.commit();
    return redirect('/dashboard')


@app.route('/logout',methods=["GET"])
def logout():
    logout_user()
    return redirect('../login')

app.run(port=5000,debug=True)