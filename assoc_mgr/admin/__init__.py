from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required
from assoc_mgr.admin.forms import Admin


bp = Blueprint("admin", __name__)


@bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin():

    form = Admin()

    redirect(url_for("roster.index"))
