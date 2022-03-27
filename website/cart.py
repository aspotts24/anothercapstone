
from flask import Blueprint, render_template, flash, url_for, redirect, request, abort, jsonify
from flask_login import current_user

from website.views import successful
from website.store import create_order
from .models import Cart
from . import db
import stripe
from .getters import get_cart_items, total_price_items

cart = Blueprint('cart', __name__)
stripe.api_key = 'sk_test_51KOEoTEAaICJ0GdRPRiVmPSZIQQ9DVtzWqeNtuevHa01p74QcR5wCNOrPdisWya0OheTal3B6kIy7Tuk987Cuk3l00n89yrf6y'

@cart.route('/website-cart', methods=['GET', 'POST'])
def website_cart():
  tip = request.form.get('tipp')
  
  total = 0
  subtotal = total_price_items()

  if tip != type(int) or tip != type(float):
    tip = 0
    total = total_price_items()
  else:
    total = total_price_items() + float(tip)
  
  new_total = str(total)
  

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
    create_order(get_cart_items(), current_user)
    return redirect(session.url, code=303)
