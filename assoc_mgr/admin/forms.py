from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired


class Admin(FlaskForm):
    submit = SubmitField("Submit button")
