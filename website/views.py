# create standard routes


from distutils.command.config import config
from flask import Blueprint, render_template, flash, request, request_started, session, url_for, redirect
from flask_login import login_required, current_user
import stripe
# added import for 'Items' table
from .models import Items, Cart
from . import db


views = Blueprint('views', __name__)
stripe.api_key = 'sk_test_51KOEoTEAaICJ0GdRPRiVmPSZIQQ9DVtzWqeNtuevHa01p74QcR5wCNOrPdisWya0OheTal3B6kIy7Tuk987Cuk3l00n89yrf6y'

@views.route('/', methods=['GET', 'POST'])
def home():
  rows = Cart.query.filter(Cart.id).count()
  return render_template("home.html", user=current_user, rows=rows)

@views.route('/menu', methods=['GET', 'POST'])
def menu():
    rows = Cart.query.filter(Cart.id).count()
    return render_template('menu.html', user=current_user, items=get_items(), rows=rows)

@views.route('/item/<int:id>', methods=['GET', 'POST'])
def item(id):
  if request.method == 'POST':
    name = request.form.get('name')
    price = request.form.get('price')
    cart_item = Cart(name=name, price=price)
    db.session.add(cart_item)
    db.session.commit()
    flash('Added to cart!', category='success')
    return redirect(url_for('views.cart'))
  else:
    rows = Cart.query.filter(Cart.id).count()
    return render_template('item.html', user=current_user, current_item=get_items()[id - 1], rows = rows)

@views.route('/cart', methods=['GET', 'POST'])
def cart():
  rows = Cart.query.filter(Cart.id).count()
  return render_template('cart.html', user=current_user, item=get_cart_items(), rows=rows)

@views.route('/create-checkout-session', methods=['POST'])
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
    cancel_url='http://127.0.0.1:5000/cart',
  )
    return redirect(session.url, code=303)

@views.route('/successful', methods=['GET', 'POST'])
def successful():
  rows = Cart.query.filter(Cart.id).count()
  return render_template('successful.html', user=current_user, rows=rows)

@views.route('/admin', methods=['POST', 'GET'])
def admin():
  if request.method == 'POST':
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    add_item = Items(name=name, price=price, description=description)
    db.session.add(add_item)
    db.session.commit()
    flash('Added to Menu', category='success')
    return redirect(url_for('views.admin'))
  user_id = current_user.id
  if user_id != 1:
    return redirect(url_for('views.home'))
  else:
    rows = Cart.query.filter(Cart.id).count()
    return render_template('admin.html', user=current_user, items=get_items(), rows=rows)

@views.route('/remove_menu_item/<int:id>')
def remove_menu_item(id):
  item_to_delete = Items.query.get_or_404(id)
  try:
    db.session.delete(item_to_delete)
    db.session.commit()
    ids = [id[0] for id in Items.query.with_entities(Items.id).all()] # fixed
    new_id = 1
    for i in ids:
      _id = Items.query.get(i)
      _id.id = new_id
      new_id += 1
      db.session.commit()
    flash('Item removed from menu')
    return redirect(url_for('views.admin'))
  except:
    flash('Problem removing item from cart')
    return redirect(url_for('views.admin'))

def get_items():
  ids = [id[0] for id in Items.query.with_entities(Items.id).all()] # fixed
  test_items = []
  for id in ids:
    item = Items.query.filter_by(id=id).first()
    grabber = {'id': 0, 'name': '', 'price': 0, 'desc': '', 'img': '', 'toppings': ['']}
    grabber['id'] = id
    grabber['name'] = item.name
    grabber['price'] = item.price
    grabber['desc'] = item.description
    grabber['img'] = item.item_image
    test_items.append(grabber)
  return test_items

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

    
