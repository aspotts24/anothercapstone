from .models import Cart, Store, Item, Employee, Option, Order
from . import db
import smtplib
from email.message import EmailMessage
from flask import flash, session

def get_cart_items():
  return session['cart']

"""   ids = [id[0] for id in Cart.query.with_entities(Cart.id).all()]
  test_cart_items = []
  names = []
  for id in ids:
    cart = session['cart']
    grabber = {'id': 0, 'name': '', 'price': 0, 'quantity': 0}
    grabber['id'] = id
    grabber['price'] = cart['price']
    grabber['quantity'] = cart['quantity']
    grabber['name'] = cart['name']
    for _name in names:
      if _name == cart.name:
        grabber['quantity'] += 1
        for _item in range(len(test_cart_items)):
          if test_cart_items[_item]['name'] in names and test_cart_items[_item]['quantity'] < grabber['quantity'] and grabber['name'] == test_cart_items[_item]['name']:
            del test_cart_items[_item]
            break
    names.append(cart.name)
    test_cart_items.append(grabber)
  return test_cart_items """

def total_price_items():
  total = 0
  prices = []
  for i in session['cart']:
    prices.append(float(i['price']) * i['quantity'])
    
  for price in prices:
    total = total + price
  return total

# helper function for multiple functions in the program
def get_items():
  # variable 'ids' finds how many ids there are inside the item table
  ids = [id[0] for id in Item.query.with_entities(Item.id).all()]
  # we return test_items but it is inited as an empty list
  test_items = []
  # for every id inside of variable 'ids'
  for id in ids:
    # declare variable 'item' as the table 'item's column values where the id is
    # the same as id being evaluated by the for loop (taken by variable ids).
    item = Item.query.filter_by(id=id).first()
    # declare starting key values (these values dont matter at all they will be replaced below)
    grabber = {'id': 0, 'name': '', 'price': 0, 'desc': '', 'img': '', 'category': 0, 'options': ''}
    # replace values that dont matter in grabber with values from item
    grabber['id'] = item.id
    grabber['name'] = item.name
    grabber['price'] = item.price
    grabber['desc'] = item.description
    grabber['img'] = item.item_image
    grabber['category'] = item.category
    # append grabber to test_items (which we return)
    test_items.append(grabber)
  return test_items

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
    grabber = {'id': 0, 'first_name': '', 'email': 0, 'password': '', 'phone': '', 'store_id': 0}
    grabber['id'] = employee.id
    grabber['first_name'] = employee.first_name
    grabber['email'] = employee.email
    grabber['password'] = employee.password
    grabber['phone'] = employee.phone
    grabber['store_id'] = employee.store_id
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

def get_orders():
  ids = [id[0] for id in Order.query.with_entities(Order.id).all()]
  all_orders = {}
  for id in ids:
    order = Order.query.filter_by(id=id).first()
    grabber = {'id': 0, 'store_id': 0, 'session_id': '', 'options': [], 'customer_name': '', 'name': '', 'quantity': 0, 'stat': 1}
    grabber['id'] = order.id
    grabber['store_id'] = order.store_id
    grabber['session_id'] = order.session_id
    grabber['options'] = order.options.split(",")
    grabber['customer_name'] = order.customer_name
    grabber['name'] = order.name
    grabber['quantity'] = order.quantity
    grabber['stat'] = order.stat
    # Places orders into a dictionary based on cart session to keep them orderly
    try:
      if grabber['session_id'] in all_orders and grabber['stat'] < 3:
        all_orders[grabber['session_id']] += [{'id': grabber['id'], 'store_id': grabber['store_id'], 'options': grabber['options'],'name': grabber['name'], 'quantity': grabber['quantity'], 'stat': grabber['stat'], 'customer_name': grabber['customer_name']}]
      elif grabber['session_id'] not in all_orders and grabber['stat'] < 3:
        all_orders[grabber['session_id']] = [{'id': grabber['id'], 'store_id': grabber['store_id'], 'options': grabber['options'],'name': grabber['name'], 'quantity': grabber['quantity'], 'stat': grabber['stat'], 'customer_name': grabber['customer_name']}]
    except:
      flash(f"Error grabbing order: {grabber['session_id']}")
  return all_orders

def alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    # your email and password
    user = 'huntersautosender@gmail.com'
    password = 'reukwfjkcrqizqta'
    
    # setting message subject and receiver to whatever values are passed
    msg['subject'] = subject
    msg['to'] = to
    msg['from'] = user
    
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

def getItemsInCart():
    # rows = Cart.query.filter(Cart.id).count()
    try:
      rows = len(session['cart'])
      return rows
    except:
      return 0