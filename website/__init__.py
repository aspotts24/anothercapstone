
from ast import Try
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


# define database
db = SQLAlchemy()
DB_NAME = "database.db"

UPLOAD_FOLDER = 'website/static/pictures'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def create_app():
    app = Flask(__name__) # referring to the flask webserver as app
    app.config['SECRET_KEY'] = 'hardtoguessstring' # secret key can be stored in package for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # set location of database (f string works 3.6 and up)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # stop deprecation warning
    # stripe keys
    app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51KOEoTEAaICJ0GdRefNXSBVkweBrxnstsqv3MbIqp2KGAsVettXtQ5oIp90F4H4GNYQjIJai81V8MZGweNA4eJkm00uxtJBQwa'
    app.config['STRIPE_SECRET_KEY'] = 'sk_test_51KOEoTEAaICJ0GdRPRiVmPSZIQQ9DVtzWqeNtuevHa01p74QcR5wCNOrPdisWya0OheTal3B6kIy7Tuk987Cuk3l00n89yrf6y'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    
    db.init_app(app) # init database

    # importing views and auth from views and auth .py
    from .views import views # found in views.py
    from .auth import auth # found in auth.py
    from .menu import menu
    from .admin import admin
    from .store import store
    from .cart import cart
    app.register_blueprint(views, url_prefix='/') # registering blueprints routes from views.py
    app.register_blueprint(auth, url_prefix='/') # registering blueprints routes from auth.py
    app.register_blueprint(menu, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')
    app.register_blueprint(store, url_prefix='/')
    app.register_blueprint(cart, url_prefix='/')


    from .models import User, Store, Employee # ensures database classes are created when starting up server
    create_database(app) # created database
    
    # login stuff
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        try:
            if session['account-type'] == 'User':
                return User.query.get(int(id))
            elif session['account-type'] == 'Store':
                return Store.query.get(int(id))
            elif session['account-type'] == 'Employee':
                return Employee.query.get(int(id))
        except:
            return User.query.get(int(id))

    return app # end of create app


# the function that creates database if its not already
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        # print('Created Database!')
