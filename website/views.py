# create standard routes
# contains:
# 1. home function (home.html)
# 2. successful function (successful.html)


from flask import Blueprint, render_template, request
from flask_login import current_user
import stripe
from .models import Cart, Store

from .getters import get_stores, getItemsInCart


# this is our blueprint for views. this also needs to be declared in init
views = Blueprint('views', __name__)
STRIPE_WEBHOOK_SECRET = 'whsec_79f5f5d2ec674236722c5dc4d461543437221a3fb88053eb8ab106cdd30295c0'

# this is our function for home.html it holds all python code needed in order to properly display the page
@views.route('/')
def home():
    return render_template("home.html", user=current_user, rows=getItemsInCart())

# this is our function for successful.html it holds all python code needed in order to properly display the page
# this function needs a lot of work as this page will contain much more information.
@views.route('/successful', methods=['POST', 'GET'])
def successful():
    return render_template('successful.html', user=current_user, rows = getItemsInCart())

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

# TODO Webhook to read completed purchases, currently does not work.
@views.route("/webhook", methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )

    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fulfill the purchase...
        print('Order fulfilled!')

    return 'Success', 200
