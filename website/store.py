from multiprocessing.sharedctypes import Value
import re
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Employee, Cart, Order
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
# this is why user mixin needed to be added to user model
from flask_login import current_user
from .getters import get_employees

store = Blueprint('store', __name__)


@store.route('/edit-employees', methods=['POST', 'GET'])
def edit_employees():
  # if store adds a new employee
  if request.method == 'POST':
    email = request.form.get('email')
    phone = request.form.get('phone')
    first_name = request.form.get('first_name')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    # search table by email entered
    employee = Employee.query.filter_by(email=email).first()
    # check if email is already inside of table and all info meets requirements below
    if employee:
      # if it is flask this message
      flash('Email already exists.', category='error')
    elif len(email) < 4:
      flash('Email must be greater than 3 characters.', category='error')
    elif len(first_name) < 2:
      flash('First name must be greater than 1 character.', category='error')
    elif password1 != password2:
      flash('Passwords don\'t match.', category='error')
    elif len(password1) < 7:
      flash('Password must be at least 7 characters.', category='error')
    else:
      # create new user by passing data into variable called 'new_employee'
      new_employee = Employee(email=email,
      first_name=first_name,
      phone=phone,
      password=generate_password_hash(password1, method='sha256'))
      # pass new_employee into database
      db.session.add(new_employee)
      # save database with new_employee passed
      db.session.commit()
      flash('Employee created!', category='success')
      return redirect(url_for('store.edit_employees'))
      # end of post request
  # rows to track cart quantity
  rows = Cart.query.filter(Cart.id).count()
  return render_template('editemployees.html', user=current_user, account=get_employees(), rows=rows)

@store.route('/remove_employee/<int:id>')
def remove_employee(id):
  option_to_delete = Employee.query.get_or_404(id)
  try:
    db.session.delete(option_to_delete)
    db.session.commit()
    
    # reassign ids so there in a good order
    ids = [id[0] for id in Employee.query.with_entities(Employee.id).all()] # fixed
    new_id = 1
    for i in ids:
      _id = Employee.query.get(i)
      _id.id = new_id
      new_id += 1
      db.session.commit()

    flash('Employee removed')
    return redirect(url_for('store.edit_employees'))
  except:
    flash('Problem removing Employee')
    return redirect(url_for('store.edit_employees'))

@store.route('/current-orders', methods=['POST', 'GET'])
def current_orders():
  orders = get_orders()
  for person in orders:
    for item in orders[person]:
      if item['stat'] >= 3:
        remove_order(item['id'])
        orders = get_orders()
  # Pushes the order status one step ahead
  if request.method == 'POST':
    for person in orders:
      if request.form['push-status'] == person:
        for item in orders[person]:
          Order.query.get(item['id']).stat += 1
          db.session.commit()
          orders = get_orders()

  return render_template('currentorders.html', user=current_user, orders=orders)

@store.route('/remove_order/<int:id>')
def remove_order(id):
  order_to_delete = Order.query.get_or_404(id)
  try:
    db.session.delete(order_to_delete)
    db.session.commit()
    
    # reassign ids so there in a good order
    ids = [id[0] for id in Order.query.with_entities(Order.id).all()] # fixed
    new_id = 1
    for i in ids:
      _id = Order.query.get(i)
      _id.id = new_id
      new_id += 1
      db.session.commit()

    return redirect(url_for('store.current_orders'))
  except:
    flash('Problem removing Order')
    return redirect(url_for('store.current_orders'))


def get_orders():
  ids = [id[0] for id in Order.query.with_entities(Order.id).all()]
  all_orders = {}
  for id in ids:
    order = Order.query.filter_by(id=id).first()
    grabber = {'id': 0, 'customer_name': '', 'name': '', 'quantity': 0, 'stat': 1}
    grabber['id'] = order.id
    grabber['customer_name'] = order.customer_name
    grabber['name'] = order.name
    grabber['quantity'] = order.quantity
    grabber['stat'] = order.stat
    # Places orders into a dictionary based on customer to keep them orderly
    if grabber['customer_name'] in all_orders:
      all_orders[grabber['customer_name']] += [{'id': grabber['id'],'name': grabber['name'], 'quantity': grabber['quantity'], 'stat': grabber['stat']}]
    else:
      all_orders[grabber['customer_name']] = [{'id': grabber['id'],'name': grabber['name'], 'quantity': grabber['quantity'], 'stat': grabber['stat']}]
  return all_orders

def create_order(items, user):
  for item in items:
    # Gives customers unique names (Their first name plus website ID) incase multiple people with same name place orders
    new_order = Order(customer_name=f"{user.first_name} ({user.id})", 
    stat=1, 
    name=item['name'], 
    quantity=item['quantity'])
    db.session.add(new_order)
  db.session.commit()
  return