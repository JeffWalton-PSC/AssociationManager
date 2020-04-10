import functools
import logging

from flask import current_app, abort, send_file, make_response
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
#from assoc_mgr import db,bcrypt, ldap_manager, login_manager #imported from __init__.py
#from assoc_mgr.auth.forms import LDAPLoginForm
#from assoc_mgr.models import UserLDAP
#from flask_login import login_user, current_user, logout_user, login_required, UserMixin

from werkzeug.security import check_password_hash, generate_password_hash

from assoc_mgr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
users ={}
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

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

