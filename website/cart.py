from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import current_user
from .models import Cart
from . import db
import stripe


cart = Blueprint('cart', __name__)
stripe.api_key = 'sk_test_51KOEoTEAaICJ0GdRPRiVmPSZIQQ9DVtzWqeNtuevHa01p74QcR5wCNOrPdisWya0OheTal3B6kIy7Tuk987Cuk3l00n89yrf6y'

@cart.route('/website-cart', methods=['GET', 'POST'])
def website_cart():
  tip = request.form.get('tipp')
  
  total = 0
  subtotal = total_price_items()

  if tip == '' or tip == None:
    tip = 0
    total = total_price_items()
  else: 
    total = total_price_items() + float(tip)
  
  rows = Cart.query.filter(Cart.id).count()
  return render_template('cart.html', user=current_user, item=get_cart_items(), rows=rows, total='{:,.2f}'.format(total), subtotal='{:,.2f}'.format(subtotal),
   tip='{:,.2f}'.format(float(tip)))


@cart.route('/delete/<int:id>')
def delete(id):
  item_to_delete = Cart.query.get_or_404(id)
  try:
    db.session.delete(item_to_delete)
    db.session.commit()
    flash('Item removed from cart')
    return redirect(url_for('cart.website_cart'))
  except:
    flash('Problem removing item from cart')
    return redirect(url_for('cart.website_cart'))


@cart.route('/clearcart')
def clearcart():
  num_of_items_in_cart = [id[0] for id in Cart.query.with_entities(Cart.id).all()]
  for item in num_of_items_in_cart:
    item_to_delete = Cart.query.get_or_404(item)
    try:
      db.session.delete(item_to_delete)
      db.session.commit()
    except:
      flash('Problem removing ', item_to_delete.name, ' from cart.' )
  flash('All items removed from cart!')
  return redirect(url_for('cart.website_cart'))


@cart.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    session = stripe.checkout.Session.create(
    line_items=[{
      'price_data': {
        'currency': 'usd',
        'product_data': {
          'name': 'Pizza',
        },
        'unit_amount': 1999,
      },
      'quantity': 1,
    }],
    mode='payment',
    success_url='http://127.0.0.1:5000/successful',
    cancel_url='http://127.0.0.1:5000/website-cart',
  )
    return redirect(session.url, code=303)


def get_cart_items():
  ids = [id[0] for id in Cart.query.with_entities(Cart.id).all()]
  test_cart_items = []
  names = []
  for id in ids:
    cart = Cart.query.filter_by(id=id).first()
    grabber = {'id': 0, 'name': '', 'price': 0, 'quantity': 0}
    grabber['id'] = id
    grabber['price'] = cart.price
    grabber['quantity'] = cart.quantity
    grabber['name'] = cart.name
    for _name in names:
      if _name == cart.name:
        grabber['quantity'] += 1
        for _item in range(len(test_cart_items)):
          if test_cart_items[_item]['name'] in names and test_cart_items[_item]['quantity'] < grabber['quantity'] and grabber['name'] == test_cart_items[_item]['name']:
            del test_cart_items[_item]
            break
    names.append(cart.name)
    test_cart_items.append(grabber)
  return test_cart_items

def total_price_items():

  ids = [id[0] for id in Cart.query.with_entities(Cart.id).all()]
  total = 0
  prices = []
  for id in ids:
    item = Cart.query.filter_by(id=id).first()
    prices.append(item.price)
    
  for price in prices:
    total = total + price
  return total

# TODO Used to create orders for stores/employees to view/update
def create_order(price, name):
  return

