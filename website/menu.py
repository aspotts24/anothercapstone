# blueprint for all menu related functions go in this file the blueprint itslef is named 'menu'

from unicodedata import category
from click import option
from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import current_user
from . import db
from .models import Cart, Employee, Item, Option, Store
from .getters import get_items

# blueprint named menu, this needs to be added to __init__
menu = Blueprint('menu', __name__)

# this is the function for menu.html(no overloads)
# had to rename function from 'menu' to 'website_menu'(function cannot shadow blueprint name)
# return:
# 1. menu.html
# 2. current_user (dont have to pass this if we dont require login)
# 3. get_items function (description at bottom of page)
# 4. rows (which returns the number of items currently in cart)
@menu.route('/website-menu', methods=['GET', 'POST'])
def website_menu():
  rows = Cart.query.filter(Cart.id).count()
  return render_template('menu.html', user=current_user, items=get_items(), rows=rows)


# this is the function for item/id.html (pass id to reference it inside the weblink)
# post request is for when user adds item to cart. (the rest of the implemetation is inside html file)
# return:
# item.html
# current_user
# get_item()[id-1] (minus one becasue of how item.id is being collected)
# rows for the number of items in cart
@menu.route('/item/<int:id>', methods=['GET', 'POST'])
def item(id):
  # start post request if user clicks on add to cart button
  if request.method == 'POST':
    name = request.form.get('name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    cart_item = Cart(name=name, price=price, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()
    flash('Added to cart!', category='success')
    return redirect(url_for('menu.website_menu'))
    # end of post request
  else:
    # return the html along with the info to be displayed
    rows = Cart.query.filter(Cart.id).count()
    
    return render_template('item.html', user=current_user, current_item=get_items()[id-1], options=get_options(), rows=rows)


def get_stores():
  ids = [id[0] for id in Store.query.with_entities(Store.id).all()]
  all_stores = []
  for id in ids:
    store = Store.query.filter_by(id=id).first()
    grabber = {'id': 0, 'first_name': '', 'email': 0, 'password': '', 'phone': ''}
    grabber['id'] = store.id
    grabber['first_name'] = store.address
    grabber['email'] = store.email
    grabber['password'] = store.password
    grabber['phone'] = store.phone
    all_stores.append(grabber)
  return all_stores

def get_employees():
  ids = [id[0] for id in Employee.query.with_entities(Employee.id).all()]
  all_employees = []
  for id in ids:
    employee = Employee.query.filter_by(id=id).first()
    grabber = {'id': 0, 'first_name': '', 'email': 0, 'password': '', 'phone': ''}
    grabber['id'] = employee.id
    grabber['first_name'] = employee.first_name
    grabber['email'] = employee.email
    grabber['password'] = employee.password
    grabber['phone'] = employee.phone
    all_employees.append(grabber)
  return all_employees

def get_options():
    ids = [id[0] for id in Option.query.with_entities(Option.id).all()]
    all_options = []
    for id in ids:
        option = Option.query.filter_by(id=id).first()
        grabber = {'id':0, 'name':'', 'price':0, 'description': '', 'category': 0}
        grabber['id'] = option.id
        grabber['name'] = option.name
        grabber['price'] = option.price
        grabber['description'] = option.description
        grabber['category'] = option.category
        all_options.append(grabber)
    return all_options
