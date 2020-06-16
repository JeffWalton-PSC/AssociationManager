from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class Login(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
