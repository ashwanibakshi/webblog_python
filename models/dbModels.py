from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped,MappedColumn
from flask_login import UserMixin
import datetime

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)




class Contact(db.Model):
    sno: Mapped[int]        = MappedColumn(primary_key=True,autoincrement = True)
    name: Mapped[str]       = MappedColumn(nullable=False)
    email: Mapped[str]      = MappedColumn(nullable=False)
    msg: Mapped[str]        = MappedColumn(nullable=False)
    location: Mapped[str]   = MappedColumn(nullable=False)
    subject: Mapped[str]    = MappedColumn(nullable=False)
    phno : Mapped[str]      = MappedColumn(nullable=False)
    date:Mapped[datetime.datetime] = MappedColumn(nullable=False)


class Users(UserMixin,db.Model):
   id   :Mapped[int]           = MappedColumn(primary_key=True,autoincrement=True)
   name  : Mapped[str]         = MappedColumn(nullable=False)
   email : Mapped[str]         = MappedColumn(nullable=False)
   password : Mapped[str]      = MappedColumn(nullable=False)
   image : Mapped[str]         = MappedColumn(nullable=True)


class Article(db.Model):
    id      : Mapped[int]         = MappedColumn(primary_key=True,autoincrement=True)
    title   : Mapped[str]         = MappedColumn(nullable=False)
    content : Mapped[str]         = MappedColumn(nullable=False)  
    slug    : Mapped[str]         = MappedColumn(nullable=False)  
    authorId: Mapped[int]         = MappedColumn(nullable=False)
    date    : Mapped[str]         = MappedColumn(nullable=True) 
