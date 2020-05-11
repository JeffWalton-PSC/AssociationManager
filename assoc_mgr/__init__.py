import os

from flask import Flask
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
#from flask_bcrypt import Bcrypt #Library for encryption
#from flask_login import LoginManager
#from assoc_mgr.config import Config
#from flask_ldap3_login import LDAP3LoginManager
#from flask_ldap3_login.forms import LDAPLoginForm
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from loguru import logger




# bcrypt = Bcrypt()

# login_manager = LoginManager()
# ldap_manager = LDAP3LoginManager()
# login_manager.login_view = 'login.login'
# login_manager.login_message_category = 'info'

from sqlalchemy import create_engine
engine = create_engine('sqlite:///data/Campus6_mock.db?check_same_thread=False')
connection = engine.connect()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.path.join(app.instance_path, 'data.sqlite')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    logger.add(os.path.join(app.instance_path, "logs/assoc_mgr.log"), 
        rotation="monthly", 
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {name} | {message}"
        )
    logger.info(f"Start")

    bootstrap = Bootstrap(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)
    
    db = SQLAlchemy(app) 

    # bcrypt.init_app(app)
    # login_manager.init_app(app)
    # ldap_manager.init_app(app)

    # from assoc_mgr.add.routes import add
    # from assoc_mgr.main.routes import homepage
    # from assoc_mgr.misc.routes import misc

    # app.register_blueprint(add)
    # app.register_blueprint(homepage)
    # app.register_blueprint(misc)


    #from . import db
    #db.init_app(app)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    from . import errors
    app.register_blueprint(errors.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import roster
    app.register_blueprint(roster.bp)

    return app

