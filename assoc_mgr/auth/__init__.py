import functools
import logging
from datetime import datetime
from loguru import logger


from flask import current_app, abort, send_file, make_response
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
#from assoc_mgr import db,bcrypt, ldap_manager, login_manager #imported from __init__.py
#from assoc_mgr.auth.forms import LDAPLoginForm
#from assoc_mgr.models import UserLDAP
#from flask_login import login_user, current_user, logout_user, login_required, UserMixin
from flask_login import login_user, logout_user, login_required, current_user


from werkzeug.security import check_password_hash, generate_password_hash

from .. import db
from ..models import User

#from assoc_mgr import ldap_manager, login_manager
#from flask_ldap3_login import AuthenticationResponseStatus

from assoc_mgr.auth.forms import Login
from assoc_mgr.queries import associations, yearterms, students, association_export


from assoc_mgr import connection as assoc_mgr_conn
connection = assoc_mgr_conn

df_yearterm = yearterms(connection)
df_association = associations(connection)


bp = Blueprint('auth', __name__, url_prefix='/auth')
#users ={}
logging.basicConfig(level=logging.DEBUG)

# @ldap_manager.save_user
# def save_user(dn, username, data, memberships):
#         user = UserLDAP(dn, username, data)
#         users[dn] = user
#         return user
 
# @login_manager.user_loader
# def load_user(id):
#     #return UserLDAP.query.get(int(id))
#     if id in users:
#         return users[id]
#     return None

# @Login.route("/login", methods =['GET', 'POST']) 
# def login():
#     #if current_user.is_authenticated:
#         #return redirect(url_for('main.home'))
#     #form = LoginForm()
#     form = LDAPLoginForm()
#     if form.validate_on_submit():
#         login_user(form.user, remember=form.remember.data)
#         next_page = request.args.get('next')
#         return redirect(next_page) if next_page else redirect(url_for('home.home'))
#     return render_template('loginTest.html', title='login', form = form)

# @Login.route("/logout")
# def logout():
#     logout_user()
#     return redirect(url_for('home.home'))

@bp.route('/')
def index():
   return redirect(url_for('auth.login'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    
    form = Login()

    if form.validate_on_submit():
        username=form.username.data.lower()
        user = User.query.filter_by(username=username).first()
        password = form.password.data

        if user is not None and user.verify_password(password):
            session.clear()
            login_user(user)
            session['yearterm_list'] = [tuple(t) for t in df_yearterm[['YEARTERM', 'YEARTERM']].to_numpy()]
            session['association_list'] = [tuple(a) for a in df_association.to_numpy()]
            logger.info(f"{username} (user_id={session['user_id']}) logged in.")
            return redirect(url_for('roster.index'))

        flash('Invalid username or password.')
        logger.error(f"{username}: Incorrect username or password.")

    return render_template('auth/login.html', form=form )


# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = get_db().execute(
#             'SELECT * FROM user WHERE id = ?', (user_id,)
#         ).fetchone()


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    logger.info(f"{current_user.username} - logged out.")
    session.clear()
    return redirect(url_for('auth.login'))


# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))
#         return view(**kwargs)

#     return wrapped_view

