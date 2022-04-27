# blueprint for all menu related functions go in this file the blueprint itslef is named 'menu'

from datetime import datetime
from unicodedata import category
from click import option
from flask import Blueprint, render_template, flash, url_for, redirect, request, session
from flask_login import current_user
from . import db
from .models import Cart, Employee, Item, Option, Store
from .getters import get_items, getItemsInCart, get_stores, get_employees, get_options, get_discounts
import random

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
  
  return render_template('menu.html', user=current_user, items=get_items(), rows = getItemsInCart(), getDis= get_discounts())


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
    price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity'))
    options = request.form.getlist('options')
    # Adds option price to the item in the cart
    i = 0
    for o in options:
      temp = o.split("|")
      options[i] = temp[0]
      price += float(temp[1])
      i+=1

    for item in session['cart']:
      if item['name'] == name and item['options'] == options:
        item['quantity'] += 1
        session.modified = True
        return redirect(url_for('menu.website_menu'))
    session['cart'] += [{'name': name, 'price': price, 'quantity': quantity, 'id': 0, 'options': options}]
    """ cart_item = Cart(name=name, price=price, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()
    flash('Added to cart!', category='success') """
    return redirect(url_for('menu.website_menu'))
    # end of post request
  else:
    return render_template('item.html', user=current_user, current_item=get_items()[id-1], options=get_options(), rows = getItemsInCart())

