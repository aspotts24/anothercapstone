# database models

from locale import currency

from sqlalchemy import PrimaryKeyConstraint
from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

# new Items class in database.db
class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    option1price = db.Column(db.Integer)
    option2price = db.Column(db.Integer)
    name = db.Column(db.String(150))
    option1Name = db.Column(db.String(150))
    option2Name = db.Column(db.String(150))
    description = db.Column(db.String(500))
    option1Description = db.Column(db.String(500))
    option2Description = db.Column(db.String(500))
    item_image = db.Column(db.String(40))

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    option1Name = db.Column(db.String(150))
    option2Name = db.Column(db.String(150))
    option1price = db.Column(db.Integer)
    option2price = db.Column(db.Integer)
    
   
  
