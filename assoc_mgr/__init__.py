import os

from flask import Flask, render_template_string
#from flask_sqlalchemy import SQLAlchemy #library for database
#from flask_bcrypt import Bcrypt #Library for encryption
from flask_login import LoginManager
#from assoc_mgr.config import Config
#from flask_ldap3_login import LDAP3LoginManager
#from flask_ldap3_login.forms import LDAPLoginForm
from flask_bootstrap import Bootstrap



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
    bootstrap = Bootstrap(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'data.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    # bcrypt.init_app(app)
    # login_manager.init_app(app)
    # ldap_manager.init_app(app)

    # from assoc_mgr.add.routes import add
    # from assoc_mgr.export.routes import exportRoute
    # from assoc_mgr.main.routes import homepage
    # from assoc_mgr.misc.routes import misc
    # from assoc_mgr.roster.routes import rosterpage
    # from assoc_mgr.errors.handlers import errors
    # from assoc_mgr.login.routes import Login

    # app.register_blueprint(add)
    # app.register_blueprint(exportRoute)
    # app.register_blueprint(homepage)
    # app.register_blueprint(misc)
    # app.register_blueprint(rosterpage)
    # app.register_blueprint(errors)
    # app.register_blueprint(Login)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import roster
    app.register_blueprint(roster.bp)
    #app.add_url_rule('/', endpoint='index')

    from flask import redirect, url_for
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))


    return app



