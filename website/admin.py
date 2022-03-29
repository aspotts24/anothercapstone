
from distutils.command.config import config
from unicodedata import category
from flask import Blueprint, render_template, flash, request, request_started, session, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import stripe
import os
from .models import Item, Cart, Store, Option
from . import db, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from werkzeug.security import generate_password_hash, check_password_hash
from .getters import get_items, get_options, get_stores, getItemsInCart


admin = Blueprint('admin', __name__)

@admin.route('/edititems', methods=['POST', 'GET'])
def create_items():
  if request.method == 'POST':
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    category = request.form.get('category')
    image = request.files['image']
    if image and allowed_file(image.filename):
      filename = secure_filename(image.filename)
      image.save(os.path.join(UPLOAD_FOLDER, filename))
    imagename = filename
    
    add_item = Item(
    name=name,
    price=price,
    description=description,
    category=category,
    item_image=imagename)

    db.session.add(add_item)
    db.session.commit()
    flash('Added to Menu', category='success')
    return redirect(url_for('admin.create_items'))
  user_id = current_user.id
  if user_id != 1:
    return redirect(url_for('views.home'))
  else:
    return render_template('edititems.html', user=current_user, items=get_items(), rows = getItemsInCart())

@admin.route('/editusers', methods=['POST', 'GET'])
def create_users():
  # if admin adds a new user
  if request.method == 'POST':
    # take all of this information entered by admin inside of html
    email = request.form.get('email')
    open = request.form.get('open')
    phone = request.form.get('phone')
    address = request.form.get('address')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    # search table by email entered
    store = Store.query.filter_by(email=email).first()
    # check if email is already inside of table and all info meets requirements below
    if store:
      # if it is flask this message
      flash('Email already exists.', category='error')
    elif len(email) < 4:
      flash('Email must be greater than 3 characters.', category='error')
    elif len(address) < 2:
      flash('First name must be greater than 1 character.', category='error')
    elif password1 != password2:
      flash('Passwords don\'t match.', category='error')
    elif len(password1) < 7:
      flash('Password must be at least 7 characters.', category='error')
    else:
      # create new user by passing data into variable called 'new_user'
      new_store = Store(email=email,
      address=address,
      phone=phone,
      open=open,
      password=generate_password_hash(password1, method='sha256'))
      # pass new_user into database
      db.session.add(new_store)
      # save database with new_user passed
      db.session.commit()
      flash('Account created!', category='success')
      # redirect to the same page admin was already on
      return redirect(url_for('admin.create_users'))
      # end of post request
  # rows to track cart quantity
  rows = Cart.query.filter(Cart.id).count()
  return render_template('editusers.html', user=current_user, account=get_stores(), rows=rows)

@admin.route('/addoptions', methods=['POST', 'GET'])
def addoptions():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        category = request.form.get('category')
        new_option = Option(name=name, price=price, description=description, category=category)
        db.session.add(new_option)
        db.session.commit()
        flash('Option added!', category='success')
        return redirect(url_for('admin.addoptions'))
    else:
        rows = Cart.query.filter(Cart.id).count()
        return render_template('itemoption.html', user=current_user, rows=rows, options=get_options())

@admin.route('/remove_menu_item/<int:id>')
def remove_menu_item(id):
  item_to_delete = Item.query.get_or_404(id)
  try:
    db.session.delete(item_to_delete)
    db.session.commit()
    ids = [id[0] for id in Item.query.with_entities(Item.id).all()] # fixed
    new_id = 1
    for i in ids:
      _id = Item.query.get(i)
      _id.id = new_id
      new_id += 1
      db.session.commit()
    flash('Item removed from menu')
    return redirect(url_for('admin.create_items'))
  except:
    flash('Problem removing item from cart')
    return redirect(url_for('admin.create_items'))

@admin.route('/remove_option/<int:id>')
def remove_option(id):
  option_to_delete = Option.query.get_or_404(id)
  try:
    db.session.delete(option_to_delete)
    db.session.commit()
    
    # reassign ids so there in a good order
    ids = [id[0] for id in Option.query.with_entities(Option.id).all()] # fixed
    new_id = 1
    for i in ids:
      _id = Option.query.get(i)
      _id.id = new_id
      new_id += 1
      db.session.commit()

    flash('Item removed from menu')
    return redirect(url_for('admin.addoptions'))
  except:
    flash('Problem removing item from cart')
    return redirect(url_for('admin.addoptions'))

@admin.route('/remove_user/<int:id>')
def remove_user(id):
  option_to_delete = Store.query.get_or_404(id)
  try:
    db.session.delete(option_to_delete)
    db.session.commit()
    
    # reassign ids so there in a good order
    ids = [id[0] for id in Store.query.with_entities(Store.id).all()] # fixed
    new_id = 1
    for i in ids:
      _id = Store.query.get(i)
      _id.id = new_id
      new_id += 1
      db.session.commit()

    flash('Store removed')
    return redirect(url_for('admin.create_users'))
  except:
    flash('Problem removing Store')
    return redirect(url_for('admin.create_users'))

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
