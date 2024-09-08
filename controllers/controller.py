import math
import json
from flask_bcrypt import Bcrypt
from flask import request
from flask_mail import Message
from slugify import slugify
from models.dbModels import Article, Contact, Users,db
from flask_login import LoginManager,login_required, login_user,current_user, logout_user


with open('.\config\config.json','r') as c:
    params = json.load(c) ['params']



loginManger = LoginManager()
bcrypt = Bcrypt()

def getLoginManager():
   return loginManger

@loginManger.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=int(user_id)).first()



def getData():
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
     data ={
        "page" : "home.html",
       "params" : "Home",
       "posts" : articles ,
       "prev"  : prev ,
       "next"  : next
     } 
        
     return data

def slug(slugg):
    article = Article.query.filter_by(slug=slugg).join(Users,Article.authorId==Users.id).add_columns(Users.name,Article.id,Article.title,Article.slug,Article.content,Article.date).first()  
    # 'blog.html',params=slugg,post=article
    data={
      "page"  : 'blog.html',
      "params": slugg,
      "post"  : article
    } 
    return data


def contacts(request,mail):
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
    
    data={
       "page":"contact.html",
       "params":"Contact Us"
    }
    return data

def loginn(request):
    if(request.method=="POST"):
        users = Users.query.filter_by(email=request.form.get("email")).first() 
        if (users is not None):
            pwd  = request.form.get("password")
            if(bcrypt.check_password_hash(users.password,pwd)):
                if(request.form.get('remember') is not None):
                   login_user(users,True)
                else:   
                    login_user(users,False) 
                    data={
                       "pass":True,
                       "page":"dashboard"
                    }  
                return data
            else:
              data={
                 "pass":False,
                 "msg1":'Wrong Email Password',
                 "msg2":'danger'
               }
            return data
        else:
            data={
               "pass":False,
                 "msg1":'User Is Not Registered',
                 "msg2":'danger'
               }
        return data
    else:
       data={
          "pass":"False",
          "msg1" :""
       }
       return data
    

def registerr(request):
   print(request.method)
   if(request.method=="POST"):
      users = Users.query.filter_by(email=request.form.get('email')).first()
      if (users is not None): 
         data={
            "pass":False,
            "msg1":'User Already Registered',
            "msg2":'danger'
         } 
         return data
      else:
       user = Users(
          name     = request.form.get("name"),
          email    = request.form.get("email"),
          password = bcrypt.generate_password_hash(request.form.get("password"))
       )
       db.session.add(user)
       db.session.commit() 

       data={
          "pass":True,
          "page":'login'
       }
       return data
   else:
       data={
         "pass":False,
         "msg1":"",
         "msg2":""
        } 
       return data  
   

def dashboard():
      dashData = Article.query.filter_by(authorId=current_user.id).all()
      data={
         "page"  :'/dashboard/dashboard.html',
         "blogs" :dashData,
         "params":"DashBoard",
         "aid"   :current_user.id
      }
      return data

def addPost(request):
   if(request.method=="POST"):
        article = Article(
           title    = request.form.get("title"),
           slug     = slugify(request.form.get("slug")),
           content  = request.form.get("content"),
           authorId = request.form.get("authorId")
        )
        db.session.add(article)
        db.session.commit()
   data={
   "page"    :'/dashboard/addpost.html',
   "author"  :current_user.name,
   "authorid":current_user.id,
   "params"  :"Add Post",
   "aid"     : current_user.id
   }
   return data

def editPostt(request):
     uid = request.form.get("authorid")
     id  = request.form.get("blogid")
     postData = Article.query.filter_by(id=id,authorId=uid).first() 
     data={
        "page"  :'/dashboard/editpost.html',
        "data"  : postData,
        "params": "Edit Post",
        "aid"   : current_user.id
     }
     return data

def updatePostt(request):
    editData = Article.query.filter_by(id=request.form.get("id"),authorId=request.form.get("authorid")).first()
    editData.title   = request.form.get("title")
    editData.slug    = request.form.get("slug")
    editData.content = request.form.get("content")
    db.session.commit()
    data={
       "page":'/dashboard'
    }
    return data

def deletePostt(request):
   Article.query.filter_by(id=request.form.get('blogid'),authorId=request.form.get("authorid")).delete()
   db.session.commit()
   data={
      "page":"/dashboard"
   }
   return data