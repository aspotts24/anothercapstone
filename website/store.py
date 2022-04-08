from multiprocessing.sharedctypes import Value
import re
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Employee, Cart, Order, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
# this is why user mixin needed to be added to user model
from flask_login import current_user
from .getters import get_employees, getItemsInCart, get_orders

store = Blueprint('store', __name__)

def check_if_not_class(class_name):
  if current_user.__class__.__name__ == class_name:
    return False
  else:
    return True

@store.route('/edit-employees', methods=['POST', 'GET'])
def edit_employees():
  # Checks if logged in as store to access page
  if check_if_not_class("Store"):
    return redirect(url_for('views.home'))
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
      password=generate_password_hash(password1, method='sha256'),
      store_id=current_user.id)
      # pass new_employee into database
      db.session.add(new_employee)
      # save database with new_employee passed
      db.session.commit()
      flash('Employee created!', category='success')
      return redirect(url_for('store.edit_employees'))
      # end of post request
  # rows to track cart quantity
  return render_template('editemployees.html', user=current_user, account=get_employees(), rows = getItemsInCart())

@store.route('/remove_employee/<int:id>')

def remove_employee(id):
  # Checks if logged in as store to access page
  if check_if_not_class("Store"):
    return redirect(url_for('views.home'))

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
  # Checks if logged in as store to access page
  if check_if_not_class("Store") and check_if_not_class("Employee"):
    if current_user.id != 1:
      return redirect(url_for('views.home'))

  orders = get_orders()

  # Pushes the order status one step ahead
  if request.method == 'POST':
    for person in orders:
      if request.form['push-status'] == person:
        for item in orders[person]:
          Order.query.get(item['id']).stat += 1
          db.session.commit()
          orders = get_orders()

  return render_template('currentorders.html', user=current_user, orders=orders, rows = getItemsInCart())

@store.route('/remove_order/<int:id>')
def remove_order(id):
  # Checks if logged in as store to access page
  if check_if_not_class("Store") and check_if_not_class("Employee"):
    if current_user.id != 1:
      return redirect(url_for('views.home'))

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