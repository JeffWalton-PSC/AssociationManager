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

from werkzeug.security import check_password_hash, generate_password_hash

from assoc_mgr.db import get_db


from flask_wtf import FlaskForm
#from assoc_mgr import ldap_manager, login_manager
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
#from flask_ldap3_login import AuthenticationResponseStatus

from assoc_mgr.queries import associations, yearterms, students, association_export



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    remember =  BooleanField('Remember This Computer')


# class LDAPLoginForm(FlaskForm):
#     username = StringField('Email', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     submit = SubmitField('Login')
#     remember =  BooleanField('Remember This Computer')


    # def validate_ldap(self):
    #     logging.debug('Validating LDAPLoginForm against LDAP')
    #     logging.debug('Validate the username/password data against ldap directory')
        
    #     username = self.username.data
    #     password = self.password.data

    #     result = ldap_manager.authenticate(username, password)

    #     if result.status == AuthenticationResponseStatus.success:
    #         self.user = ldap_manager._save_user(
    #             result.user_dn,
    #             result.user_id,
    #             result.user_info,
    #             result.user_groups
    #         )
    #         return True

    #     else:
    #         self.user = None
    #         self.username.errors.append('Invalid Username.')
    #         self.password.errors.append('Invalid Password.')
    #         return False


    # def validate(self, *args, **kwargs):
    #     """
    #     Validates the form by calling `validate` on each field, passing any
    #     extra `Form.validate_<fieldname>` validators to the field validator.
    #     also calls `validate_ldap`
    #     """
    #     print("Called: validate()", self, args, kwargs)
    #     valid = FlaskForm.validate(self, *args, **kwargs)
    #     if not valid:
    #         logging.debug("Form validation failed before we had a chance to "
    #                       "check ldap. Reasons: '{0}'".format(self.errors))
    #         return valid

    #     return self.validate_ldap()

from assoc_mgr import connection as assoc_mgr_conn
connection = assoc_mgr_conn

df_yearterm = yearterms(connection)
df_association = associations(connection)


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

@bp.route('/')
def index():
   return redirect(url_for('auth.login'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    
    form = LoginForm()

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
            logger.error(f"{username}: Incorrect username.")
        # elif not check_password_hash(user['password'], password):
        #     error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['yearterm_list'] = [tuple(t) for t in df_yearterm[['YEARTERM', 'YEARTERM']].to_numpy()]
            session['association_list'] = [tuple(a) for a in df_association.to_numpy()]
            logger.info(f"{username} (user_id={session['user_id']}) logged in.")
            return redirect(url_for('roster.index'))

        flash(error)

    return render_template('auth/login.html', form=form )


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
    logger.info(f"{session['user_id']} logged out")
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

