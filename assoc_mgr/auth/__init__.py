from loguru import logger

from flask import current_app, Blueprint, flash, redirect, render_template, session, url_for
from flask_login import login_user, logout_user, login_required, current_user

# from .. import db
from ..models import User, Role, Association

from assoc_mgr.auth.forms import Login
from assoc_mgr.queries import associations, yearterms, students, association_export

from assoc_mgr import powercampus_engine


with powercampus_engine.connect() as connection:
    df_yearterm = yearterms(connection)
    df_association = associations(connection)


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@bp.route("/login", methods=("GET", "POST"))
def login():

    form = Login()

    if form.validate_on_submit():
        username = form.username.data.lower()
        user = User.query.filter_by(username=username).first()
        password = form.password.data

        if user is not None and user.verify_password(password):
            session.clear()
            login_user(user)
            logger.info(f"{username} (user_id={session['user_id']}) logged in.")
            session["yearterm_list"] = [
                tuple(t) for t in df_yearterm[["YEARTERM", "YEARTERM"]].to_numpy()
            ]
            user_role = user.role
            logger.info(f"{user.username}: role={user_role}")
            if user_role.name == "Admin":
                session["association_list"] = [tuple(a) for a in df_association.to_numpy()]
            else:
                user_assoc_list = [a.name for a in user.role.assocs]
                if not user_assoc_list:
                    logger.error(f"{user.username} user_assoc_list is empty {user_assoc_list}.")
                    flash(f"{user.username} user_assoc_list is empty {user_assoc_list}.", "error")
                    logout_user()
                    return render_template("auth/login.html", form=form)
                else:
                    session["association_list"] = [
                        tuple(a) for a in df_association.to_numpy() if a[0] in user_assoc_list
                    ]
            return redirect(url_for("roster.index"))

        flash("Invalid username or password.", "warning")
        logger.error(f"{username}: Incorrect username or password.")

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    flash("You have been logged out.")
    logger.info(f"{current_user.username} - logged out.")
    logout_user()
    session.clear()
    return redirect(url_for("auth.login"))
