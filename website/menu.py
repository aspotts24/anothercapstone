# blueprint for all menu related functions go in this file the blueprint itslef is named 'menu'

from unicodedata import category
from click import option
from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import current_user
from . import db
from .models import Cart, Employee, Item, Option, Store
from .getters import get_items, getItemsInCart, get_stores, get_employees, get_options

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
  return render_template('menu.html', user=current_user, items=get_items(), rows = getItemsInCart())


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
    return render_template('item.html', user=current_user, current_item=get_items()[id-1], options=get_options(), rows = getItemsInCart())

