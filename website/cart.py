
from flask import Blueprint, render_template, flash, url_for, redirect, request, abort, jsonify, session
from flask_login import current_user

from .models import Cart, Order
from . import db
import stripe
from .getters import get_cart_items, total_price_items, getItemsInCart, get_discounts

cart = Blueprint('cart', __name__)
stripe.api_key = 'sk_test_51KOEoTEAaICJ0GdRPRiVmPSZIQQ9DVtzWqeNtuevHa01p74QcR5wCNOrPdisWya0OheTal3B6kIy7Tuk987Cuk3l00n89yrf6y'

@cart.route('/website-cart', methods=['GET', 'POST'])
def website_cart():
  if not session.get('ordering_from'):
    return redirect(url_for('views.start_order'))

  tip = request.form.get('tipp') # get user tip input
  discount = request.form.get('discountt') # get user discount input
  
  total = 0
  subtotal = total_price_items()
  discountTotal = discountPrice(subtotal, get_discounts(), discount)

  
  #This if statement will check if the user input is an empty string or a none value. so that way the website doesn't crash.
  if tip == '' or tip == None:
    tip = 0
    total = subtotal
  else:
    total += subtotal + float(tip)
 


  #This if statement will check if the subtotal of the cart is more than $15 to apply the discount,
  # and also to check if the user input is an empty string or a none value.
  if discount == '' or discount == None:
    discountTotal = 0
  elif subtotal >= 15:
    total -= discountTotal
  


  return render_template('cart.html', user=current_user, item=get_cart_items(), rows=getItemsInCart(), total='{:,.2f}'.format(total), subtotal='{:,.2f}'.format(subtotal),
    tip='{:,.2f}'.format(float(tip)), discount = '{:,.2f}'.format(float(discountTotal)))


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
        'unit_amount': int(item['price'] * 100),
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

def create_order(items, user, session, store_id):
  # Checks if checkout id has already been used, does not add cart to orders if true
  for order in  Order.query.with_entities(Order.session_id).all():
    if order.session_id == session:
      return
  
  for item in items:
    # Gives customers unique names (Their first name plus website ID) incase multiple people with same name place orders
    temp_options = ""
    for o in item['options']:
      if o == item['options'][-1]:
        temp_options += o
        break
      temp_options += f"{o},"
    new_order = Order(customer_name=f"{user.first_name}",
    stat=0,
    session_id=session,
    store_id=int(store_id),
    options=temp_options,
    name=item['name'],
    quantity=item['quantity'])
    db.session.add(new_order)
  db.session.commit()
  return

# this is our function for successful.html it holds all python code needed in order to properly display the page
# Uses session id on success to add the order to the store side of the current orders page
@cart.route('/successful', methods=['POST', 'GET'])
def successful():
  session_id = stripe.checkout.Session.retrieve(request.args.get('session_id'))
  create_order(get_cart_items(), current_user, session_id['id'], session['ordering_from'])
  session['cart'] = []

  return render_template('successful.html', user=current_user, rows = getItemsInCart(), session=session_id)

@cart.before_request
def init_cart():
  if not session.get('cart'):
    session['cart'] = []


def discountPrice(total, discounts, getDiscount):
  
  price_discounted = 0
  discountArray = []
  discountStr = []
  dis = 0

# This for loop will go through the discounts values inside the dict from getDiscount and save it
# to the discountArray[]
  for i in discounts:
    discountArray.append(i['discount_info'] )
# This for loop will create a new dict to store the discount and the string that the next
# for loop will use to compare the user input discount with the ones that this loop created.
  for num in discountArray:
    grabber = {'discount': 0, 'string': ''}
    grabber['discount'] = num
    grabber['string'] = str(num) + '%OFF'
    discountStr.append(grabber)
# This loop will go through the string of the discountStr array to compare the strings with the user input
  for j in discountStr:
    if j['string'] == getDiscount or j['string'].lower() == getDiscount:
      dis = int(j['discount']) / 100
      price_discounted = total * dis


  return price_discounted