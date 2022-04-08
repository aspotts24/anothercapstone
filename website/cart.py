
from flask import Blueprint, render_template, flash, url_for, redirect, request, abort, jsonify, session
from flask_login import current_user

from .models import Cart, Order
from . import db
import stripe
from .getters import get_cart_items, total_price_items, getItemsInCart

cart = Blueprint('cart', __name__)
stripe.api_key = 'sk_test_51KOEoTEAaICJ0GdRPRiVmPSZIQQ9DVtzWqeNtuevHa01p74QcR5wCNOrPdisWya0OheTal3B6kIy7Tuk987Cuk3l00n89yrf6y'

@cart.route('/website-cart', methods=['GET', 'POST'])
def website_cart():
  print(session['cart'])
  tip = request.form.get('tipp')
  
  total = 0
  subtotal = total_price_items()

  if tip != type(int) or tip != type(float):
    tip = 0
    total = total_price_items()
  else:
    total = total_price_items() + float(tip)
  
  new_total = str(total)

  return render_template('cart.html', user=current_user, item=get_cart_items(), rows=getItemsInCart(), total='{:,.2f}'.format(total), subtotal='{:,.2f}'.format(subtotal),
    tip='{:,.2f}'.format(float(tip)))


@cart.route('/delete/<int:id>')
def delete(id):
  # item_to_delete = Cart.query.get_or_404(id)
  try:
    session['cart'].pop(id)
    flash('Item removed from cart')
    return redirect(url_for('cart.website_cart'))
  except:
    flash('Problem removing item from cart')
    return redirect(url_for('cart.website_cart'))


@cart.route('/clearcart')
def clearcart():
  session['cart'] = []
  flash('All items removed from cart!')
  return redirect(url_for('cart.website_cart'))


@cart.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    cart = get_cart_items()
    cart_items = []
    for item in cart:
      cart_items += [{
      'price_data': {
        'currency': 'usd',
        'product_data': {
          'name': item['name'],
        },
        'unit_amount': int(item['price'].replace('.', '')),
      },
      'quantity': item['quantity'],
    }]
    session = stripe.checkout.Session.create(
    line_items=cart_items,
    mode='payment',
    success_url='http://127.0.0.1:5000/successful?session_id={CHECKOUT_SESSION_ID}',
    cancel_url='http://127.0.0.1:5000/website-cart',
  )
    return redirect(session.url, code=303)

def create_order(items, user, session):
  # Checks if checkout id has already been used, does not add cart to orders if true
  for order in  Order.query.with_entities(Order.session_id).all():
    if order.session_id == session:
      return
  
  for item in items:
    # Gives customers unique names (Their first name plus website ID) incase multiple people with same name place orders
    new_order = Order(customer_name=f"{user.first_name}",
    stat=0,
    session_id=session,
    name=item['name'],
    quantity=item['quantity'])
    db.session.add(new_order)
  db.session.commit()
  return

# this is our function for successful.html it holds all python code needed in order to properly display the page
# Uses session id on success to add the order to the store side of the current orders page
@cart.route('/successful', methods=['POST', 'GET'])
def successful():
  session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
  create_order(get_cart_items(), current_user, session['id'])


  return render_template('successful.html', user=current_user, rows = getItemsInCart(), session=session)