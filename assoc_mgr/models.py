import ldap3
from flask import current_app
from loguru import logger

from assoc_mgr import db, login_manager


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    def __repr__(self):
        return f"<User {self.username}>"

    def verify_password(self, password):
        return authenticate(username=self.username, password=password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True, nullable=False)
    users = db.relationship("User", backref="role")
    assocs = db.relationship("Association", backref="role")

    def __repr__(self):
        return f"<Role {self.name}>"


class Association(db.Model):
    __tablename__ = "associations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    def __repr__(self):
        return f"<Role {self.name}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def authenticate(username, password):
    server = ldap3.Server(current_app.config.get("LDAP_HOST"), use_ssl=True, get_info=ldap3.ALL)

    bind_user = f"{current_app.config.get('LDAP_BIND_USER_PREFIX')}{username}"

    connection = ldap3.Connection(
        server=server,
        read_only=True,
        user=bind_user,
        password=password,
        authentication=ldap3.NTLM,
        check_names=True,
        raise_exceptions=True,
    )

    try:
        connection.bind()
        authentication_response = True
        logger.debug(f"Authentication was successful for user '{bind_user}'")

    except ldap3.core.exceptions.LDAPInvalidCredentialsResult:
        logger.debug(f"Authentication was not successful for user '{bind_user}'")
        authentication_response = False

    except Exception as e:
        logger.error(e)
        authentication_response = False

    logger.debug(f"Destroying connection at <{hex(id(connection))}>")
    connection.unbind()

    return authentication_response
