from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class Login(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    #remember =  BooleanField('Remember This Computer')


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

