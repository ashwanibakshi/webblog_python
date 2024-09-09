import math
from flask import Flask,request,render_template,redirect,flash,session, url_for
from flask_mail import Mail,Message
from flask_bcrypt import Bcrypt
from flask_login import login_required, login_user,current_user, logout_user
import json

from slugify import slugify
from controllers.controller import addPost, dashboard, deletePostt, editPostt, getData, getProfile, logOut, registerr,slug,contacts,loginn,getLoginManager, updatePostt, updateProfile
from models.dbModels import Article,Contact,Users,db



with open('.\config\config.json','r') as c:
    params = json.load(c) ['params']

app = Flask(__name__)
bcrypt = Bcrypt(app)

login_manger = getLoginManager()
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


# @login_manger.user_loader
# def load_user(user_id):
#     return Users.query.filter_by(id=int(user_id)).first()

@app.route('/',methods=["GET"])
def home():
    data2 = getData() 
    return render_template(data2["page"],params = data2["params"],posts=data2["posts"],prev=data2["prev"],next=data2["next"])

@app.route('/blog/<slugg>',methods=["GET"])
def blog(slugg):
    data = slug(slugg)
    print('123',data)
    return render_template(data["page"],params=data["params"],post=data["post"])

@app.route('/contact',methods=["GET","POST"])
def contact():
    data = contacts(request,mail)
    return render_template(data["page"],params=data["params"]) 

@app.route('/login',methods=["GET","POST"])
def login():
    data = loginn(request)
    if(data["pass"]==True):
        return redirect(data["page"])
    if(data["msg1"]):
     flash(data["msg1"],data["msg2"])
    return render_template('login.html')

@app.route('/register',methods=["GET","POST"])
def register():
    data = registerr(request)
    if(data["pass"]==True):
        return redirect(data["page"])
    else:
     flash(data["msg1"],data["msg2"]) 
     return render_template('register.html')

@app.route('/dashboard',methods=["GET"])
@login_required
def dash():
    data = dashboard()
    return render_template(data["page"],blogs=data["blogs"],params=data["params"],aid=data["aid"])

@app.route('/addpost',methods=["GET","POST"])
@login_required
def addpost():
    data = addPost(request)
    return render_template(data["page"],author=data["author"], authorId=data["authorid"],params=data["params"],aid=data["aid"])


@app.route('/editpost',methods=["POST"])
@login_required
def editPost():
     data = editPostt(request)  
     return render_template(data["page"],data=data["data"],params=data["params"],aid=data["aid"])

@app.route('/updatepost',methods=["POST"])
@login_required
def updatePost():
    data = updatePostt(request)
    return redirect(data["page"])

@app.route('/deletepost',methods=["POST"])
@login_required
def delete():
   data = deletePostt(request)
   return redirect(data["page"])


@app.route('/profile/<aid>',methods=["GET"])
@login_required
def profile(aid):
   data = getProfile(request,aid)
   return render_template(data["page"],data=data["data"],aid=data["aid"])

@app.route('/profile',methods=["POST"])
@login_required
def profilee():
    data = updateProfile(request)
    return redirect(data["page"])


@app.route('/logout',methods=["GET"])
def logout():
    data = logOut()
    return redirect(data["page"])

app.run(port=5000,debug=True)