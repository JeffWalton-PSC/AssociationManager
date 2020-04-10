import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

from datetime import datetime #Standard python library
from flask import current_app
#from assoc_mgr import  login_manager, ldap_manager #db and login_manager imported from __init__.py
from flask_login import UserMixin

#NOTICE: Throughout the python code you may see db. underlined in places such as in this file, models.py. This seems to be an error with Pylint and there is not actually anything wrong
#with the code, it still functions normally.

   
# Declare an Object Model for the user, and make it comply with the
# flask-login UserMixin mixin.



# class UserLDAP(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100))
#     def __init__(self, dn, username, data):
#         self.dn = dn
#         self.username = username
#         self.data = data

#     def __repr__(self):
#         return self.dn

#     def get_id(self):
#         return self.dn

# class User(db.Model, UserMixin): #User class - Stored in Database
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
#     password = db.Column(db.String(60), nullable=False)
#     posts = db.relationship('Post', backref='author', lazy=True)

#     def __repr__(self):
#         return f"User('{self.username}', '{self.email}', '{self.image_file}')"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
