# create standard routes
# contains:
# 1. home function (home.html)
# 2. successful function (successful.html)


from flask import Blueprint, render_template, request, session
from flask_login import current_user
import stripe
from .models import Cart, Store
from .getters import get_stores, getItemsInCart


# this is our blueprint for views. this also needs to be declared in init
views = Blueprint('views', __name__)

# this is our function for home.html it holds all python code needed in order to properly display the page
@views.route('/')
def home():
    return render_template("home.html", user=current_user, rows=getItemsInCart())

@views.route('/start-order', methods = ['POST', 'GET'])
def start_order():
    return render_template('start-order.html', user=current_user, rows = getItemsInCart(), stores=get_stores())

@views.route('/order-type/<int:id>', methods = ['POST', 'GET'])
def order_type(id):
    orderTypes = []
    store = Store.query.filter_by(id=id).first()
    if store.open == 1:
        orderTypes.append('delivery')
    elif store.open == 2:
        orderTypes.append('delivery')
        orderTypes.append('pick-up')
    return render_template('order-type.html', user=current_user, rows = getItemsInCart(), stores=get_stores()[id-1], orderTypes=orderTypes)