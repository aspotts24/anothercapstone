# create standard routes
# contains:
# 1. home function (home.html)
# 2. successful function (successful.html)

import re
from ssl import SSL_ERROR_SSL
from flask import Blueprint, render_template, request, session, abort, jsonify
from flask_login import current_user, user_accessed
import stripe, json
from .models import Cart, Order, User
from . import db


# this is our blueprint for views. this also needs to be declared in init
views = Blueprint('views', __name__)
STRIPE_WEBHOOK_SECRET = 'whsec_79f5f5d2ec674236722c5dc4d461543437221a3fb88053eb8ab106cdd30295c0'

# this is our function for home.html it holds all python code needed in order to properly display the page
@views.route('/')
def home():
  # find the number of items in cart
  rows = Cart.query.filter(Cart.id).count()
  return render_template("home.html", user=current_user, rows=rows)

# this is our function for successful.html it holds all python code needed in order to properly display the page
# this function needs a lot of work as this page will contain much more information.
@views.route('/successful', methods=['POST', 'GET'])
def successful():
  # find the number of items in cart
  rows = Cart.query.filter(Cart.id).count()
  return render_template('successful.html', user=current_user, rows=rows)

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
