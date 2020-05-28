import os

from flask import Flask
from flask import redirect, url_for
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
#from flask_ldap3_login import LDAP3LoginManager
#from flask_ldap3_login.forms import LDAPLoginForm
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from loguru import logger
from instance.config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
toolbar = DebugToolbarExtension()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
#ldap_manager = LDAP3LoginManager()

from sqlalchemy import create_engine
engine = create_engine('sqlite:///data/Campus6_mock.db?check_same_thread=False')
connection = engine.connect()


def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #app.config.from_pyfile('config.py', silent=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    logger.add(os.path.join(app.instance_path, "logs/assoc_mgr.log"), 
        rotation="monthly", 
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {name} | {message}"
        )
    logger.info(f"Start")

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar.init_app(app)
    
    #ldap_manager.init_app(app)


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

