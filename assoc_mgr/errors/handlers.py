from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


#Routes for if ERRORs occur

#403 - Permission denied for user, no authentication.
@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

#404 is page not found/does not exist.
@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

#500 Server side error, if something goes wrong on our end.
@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500