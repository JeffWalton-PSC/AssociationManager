from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired


class Roster(FlaskForm):
    yearterm = SelectField("Year.Term", choices=[], validators=[DataRequired()])
    association = SelectField("Association", choices=[], default=None, validators=[DataRequired()])
    view_roster = SubmitField("View Roster")
    delete = BooleanField("Delete")
    add_students = SubmitField("Add Students")
    delete_students = SubmitField("Delete Students")
    save_roster = SubmitField("Save as .csv")
    new_search = SubmitField("New Search")


class AddStudent(FlaskForm):
    students = SelectMultipleField(
        "Student Names", choices=[], default=(None, "Please Select Students"), validators=[]
    )
    submit = SubmitField("Add Students")
    cancel = SubmitField("Cancel")
