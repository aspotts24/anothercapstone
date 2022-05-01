from multiprocessing.sharedctypes import Value
import re, stripe
from click import option
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import Employee, Cart, Order, User, Discount
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
# this is why user mixin needed to be added to user model
from flask_login import current_user
from .getters import get_employees, getItemsInCart, get_orders, get_discounts

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

  # Seperate orders by store id
 #store_orders = []
 #if not check_if_not_class('Employee'):
 #  for order in orders:
 #    if order[0]['store_id'] == current_user.store_id:
 #      store_orders += order
 #if not check_if_not_class('Store'):
 #  for order in orders:
 #    if orders[order][0]['store_id'] == current_user.id:
 #      store_orders += [{order: orders[order]}]
 #if not check_if_not_class('User') and current_user.id == 1:
 #  store_orders = orders

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


@store.route('/add-discounts', methods=['GET','POST'])
def add_discount():

  discountList = get_discounts()

  if request.method == 'POST':
    discount = request.form.get('discountt')

    for i in discountList:
      if i['discount_info'] == int(discount):
        flash('Discount already created')
        return redirect(url_for('store.add_discount'))
  
  #adding discounts to the database
    if discount == None or discount == '':
      flash('Error creating discount')
      return redirect(url_for('store.add_discount'))
    elif int(discount) > 50:
      flash('Discount must be less than 50%')
      return redirect(url_for('store.add_discount'))

    elif len(discountList) > 0:
      flash('Only one discount can be created.')
      return redirect(url_for('store.add_discount'))
    else:
      # create new discount by passing data into variable called 'new_dicount'
      new_discount = Discount(discount_info=int(discount))
      # pass new_employee into database
      db.session.add(new_discount)
      # save database with new_discount passed
      db.session.commit()
      stripe.Coupon.create(
        id=f"{discount}OFF",
        percent_off=int(discount),
        duration="forever",
      )
      flash('Discount Created!', category='success')
      return redirect(url_for('store.add_discount'))

  return render_template('addDiscounts.html', user=current_user, discount=get_discounts())

@store.route('/remove_discount/<int:id>')
def remove_discount(id):
  option_to_delete = Discount.query.get_or_404(id)
  try:
    disc_info = option_to_delete.discount_info
    db.session.delete(option_to_delete)
    db.session.commit()
    
    # reassign ids so there in a good order
    ids = [id[0] for id in Discount.query.with_entities(Discount.id).all()] # fixed
    new_id = 1
    for i in ids:
      _id = Discount.query.get(i)
      _id.id = new_id
      new_id += 1
      db.session.commit()

    stripe.Coupon.delete(f"{disc_info}OFF")

    flash('Discount removed')
    return redirect(url_for('store.add_discount'))
  except:
    flash('Problem removing Discount')
    return redirect(url_for('store.add_discount'))

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