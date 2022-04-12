# database models


from locale import currency
from unicodedata import category

from sqlalchemy import PrimaryKeyConstraint
from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

class Employee(db.Model, UserMixin): # store employee info to show admin whos working and who will handle delivery requests
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True) # for login
    password = db.Column(db.String(150))
    phone = db.Column(db.String(150)) # for automated text about current delivery
    first_name = db.Column(db.String(150)) # admin to quicky identify employee
    onclock = db.Column(db.Integer) # config if dilvery driver is able to
    store_id = db.Column(db.Integer) # what store the employee works at

class Store(db.Model, UserMixin): # login for storefront section of website
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True) # store contact info
    password = db.Column(db.String(150))
    phone = db.Column(db.String(150)) # store contact info
    address = db.Column(db.String(150)) # helps with user ordering delivery
    open = db.Column(db.Integer) # tells customer side of website when resturant is accepting online orders

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Integer)
    description = db.Column(db.String(500))
    category = db.Column(db.Integer) # Helps create different sections of menu and similar items section
    item_image = db.Column(db.String(40))

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Integer)
    description = db.Column(db.String(500))
    category = db.Column(db.Integer)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    item_image = db.Column(db.String(40))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(200))
    options = db.Column(db.String(500))
    name = db.Column(db.String(150))
    customer_name = db.Column(db.String(150))
    quantity = db.Column(db.Integer)
    store_id = db.Column(db.Integer) # which store the order is assigned to
    stat = db.Column(db.Integer) # 1,2,3 order status accepted, on the way, completed

class Discount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discount_info = db.Column(db.Integer) # type of discount