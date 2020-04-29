from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, ValidationError



class Roster(FlaskForm):       
    yearterm = SelectField ('Year.Term', 
                        choices=[], validators=[DataRequired()])
    association = SelectField ('Association', choices=[], 
                                default = None, validators=[DataRequired()])
    view_roster = SubmitField("View Roster")
    delete = BooleanField("Delete")
    add_students = SubmitField("Add Student(s)")
    delete_students = SubmitField("Delete Student(s)")
    save_roster = SubmitField("Save as .csv")
    new_search = SubmitField("New Search")


class Export(FlaskForm):
    yearterm = SelectField ('Year.Term', 
                        choices=[], validators=[DataRequired()])
    association = SelectField ('Association', choices=[], 
                                default = None, validators=[DataRequired()])
    submit = SubmitField("DOWNLOAD")


from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response, session, redirect
from assoc_mgr.queries import associations, yearterms, association_export
from datetime import datetime

from assoc_mgr.auth import login_required
from assoc_mgr.db import get_db

bp = Blueprint('roster', __name__)

# @bp.route('/')
# def index():
#     return render_template('roster/index.html')


from assoc_mgr import connection as assoc_mgr_conn
connection = assoc_mgr_conn

today_str = datetime.now().strftime("%Y%m%d")

#df_yearterm = yearterms(connection)
#df_association = associations(connection)

@bp.route("/roster/index", methods = ['GET', 'POST'])
#@login_required #Forces user to login to navigate to roster page.
def index():

    form = Roster()
    form.yearterm.choices = session['yearterm_list']
    form.association.choices = session['association_list']

    if form.validate_on_submit():
        yearterm = form.yearterm.data
        session['yearterm'] = yearterm
        year = yearterm.split('.')[0]
        term = yearterm.split('.')[1]
        association = form.association.data
        session['association'] = association

        print(request.form)

        if 'view_roster' in request.form:
        
            df_export = association_export(year, term, association, connection)
            df_export = df_export.rename(columns={'PEOPLE_ORG_CODE_ID': 'PSC_ID'})

            if not(df_export.empty):
                result = df_export.to_dict('split')['data']
                return render_template('roster/index.html',
                    form = form,
                    association = association,
                    yearterm = yearterm,
                    title = f"{association} - {term} {year}", 
                    result = result,
                    resultlength = f"{str(len(result))} result(s) found."
                    )

            else:
                flash("No results were returned. Please try again.")
                return render_template('roster/index.html', title = 'Roster', form = form)

        elif 'add_students' in request.form:

            return render_template("/roster/add.html", association=association, yearterm=yearterm )

        else:
            flash("Error", "error")
            return render_template('/roster/index.html', title = 'Roster', form = form)
        
    else:
        return render_template('/roster/index.html', title = 'Roster', form = form)



# @bp.route("/roster", methods = ['GET', 'POST'])
# #@login_required #Forces user to login to navigate to roster page.
# def roster():

#     form = Roster()
#     form.yearterm.choices = session['yearterm_list']
#     form.association.choices = session['association_list']

#     if form.validate_on_submit():
#         yearterm = form.yearterm.data
#         year = yearterm.split('.')[0]
#         term = yearterm.split('.')[1]
#         association = form.association.data

#         df_export = association_export(year, term, association, connection)
#         df_export = df_export.rename(columns={'PEOPLE_ORG_CODE_ID': 'PSC_ID'})

#         if not(df_export.empty):
#             result = df_export.to_dict('split')['data']
#             return render_template('roster/display.html', 
#                 association = f"{association}",
#                 yearterm = f"{yearterm}",
#                 title = f"{association} - {term} {year}", 
#                 result = result,
#                 resultlength = f"{str(len(result))} result(s) found."
#                 )

#         else:
#             flash("No results were returned. Please try again.")
#             return render_template('roster/roster.html', title = 'Roster', form = form)
#     else:
#         return render_template('roster/roster.html', title = 'Roster', form = form)


# #Handler for Delete Request
# @bp.route("/roster/display", methods = ['GET', 'POST'])
# #@login_required 
# def display():

#     pscid = request.args.get('pscid')
#     lname = request.args.get('lname')
#     fname = request.args.get('fname')
#     association = request.args.get('association')
#     term = request.args.get('term')
#     year = request.args.get('year')
 
#     if request.method == 'GET':
#         sql_str = f"""
#         DELETE 
#         FROM ASSOCIATION 
#         WHERE PEOPLE_ORG_CODE_ID = '{pscid}' 
#           AND ASSOCIATION = '{association}' 
#           AND ACADEMIC_TERM = '{term}' 
#           AND ACADEMIC_YEAR = '{year}' 
#         """

#         connection.execute(sql_str)

#         flash(f"{lname}, {fname} has been deleted from {association} for {term} {year}.", "danger")

#     return redirect(url_for('roster.roster'))


# @bp.route("/roster/export", methods = ['GET', 'POST'])
# #@login_required
# def export():
    
#     yearterm = request.args.get('yearterm')
#     association = request.args.get('association')

#     form = Export(yearterm=yearterm, association=association )

#     form.yearterm.choices = session['yearterm_list']
#     form.association.choices = session['association_list']

#     if form.validate_on_submit():
#         yearterm = form.yearterm.data
#         year = yearterm.split('.')[0]
#         term = yearterm.split('.')[1]
#         association = form.association.data

#         df_export = association_export(year, term, association, connection)

#         if not(df_export.empty):
#             df_export = df_export.rename(columns={'PEOPLE_ORG_CODE_ID': 'PSC_ID'})
#             resp = make_response(df_export.to_csv(index=False))
#             resp.headers["Content-Disposition"] = ( f"attachment; filename={year}{term}_{association}_Roster_{today_str}.csv" )
#             resp.headers["content-Type"] = "text/csv"
#             return resp

#         else:
#             flash("No results were returned. Please Try again.")
 
#     return render_template('roster/export.html', title = 'Export Roster', form = form, yearterm=yearterm, association=association)


# from flask_wtf import FlaskForm
# from wtforms.validators import DataRequired
from wtforms import SubmitField, SelectField, SelectMultipleField

class AddStudentForm(FlaskForm):
    yearterm = SelectField ('Year.Term', 
                        choices=[], validators=[DataRequired()])
    association = SelectField ('Association', choices=[], 
                                default = None, validators=[DataRequired()])
    student = SelectMultipleField('Student Names', choices = [], 
                                default = (None, 'Please Select Student(s)'), validators=[DataRequired()])
    submit = SubmitField('Add Student(s)') 


from flask import render_template, url_for, flash, redirect, Blueprint
#from assoc_mgr.add.forms import AddStudentForm
from assoc_mgr.queries import students, associations, yearterms, association_members
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import pandas as pd



today = datetime.now()
now = str(today.year)
one_year_ago = str(today.year - 1)
two_years_ago = str(today.year - 2)


@bp.route("/roster/add", methods =['GET', 'POST'])
#@login_required #Forces user to login to navigate to update page.
def add():

    form = AddStudentForm()

    df_student = students(now, one_year_ago, connection)
    form.yearterm.choices = session['yearterm_list']
    form.association.choices = session['association_list']
    form.student.choices = [tuple(s) for s in df_student[['PEOPLE_CODE_ID', 'STUDENT']].to_numpy()]


    if form.validate_on_submit():

        yearterm = form.yearterm.data
        session['yearterm'] = yearterm
        year = yearterm.split('.')[0]
        term = yearterm.split('.')[1]
        association = form.association.data
        session['association'] = association
        
        add_list = form.student.data

        assoc_members = association_members(year, term, association, connection)

        if len(add_list) > 0:

            insert_sql = """
				INSERT INTO ASSOCIATION
					(
					PEOPLE_ORG_CODE, 
					PEOPLE_ORG_ID, 
					PEOPLE_ORG_CODE_ID, 
					ASSOCIATION, 
					ACADEMIC_YEAR, 
					ACADEMIC_TERM, 
					ACADEMIC_SESSION, 
					OFFICE_HELD,
					CREATE_DATE, 
					CREATE_TIME, 
					CREATE_OPID, 
					CREATE_TERMINAL, 
					REVISION_DATE, 
					REVISION_TIME, 
					REVISION_OPID, 
					REVISION_TERMINAL, 
					ABT_JOIN
					)
				VALUES """

            first = True
            exists_list = []
            for student in add_list:
                # test if student already exists in ASSOCIATION table. 
                if student in assoc_members:
                    exists_list.insert(student)
                    continue
                today = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
                if first:
                    first = False
                else:
                    insert_sql += ','

                insert_val = f"""
				(
					'{student[:1]}', 
					'{student[1:]}', 
					'{student}', 
					'{association}', 
					'{year}', 
					'{term}', 
					'', 
					'',
					'{today}', 
					'{today}', 
					'ASSOCMGR', 
					'0001', 
					'{today}', 
					'{today}', 
					'ASSOCMGR', 
					'0001', 
					'*'
				) """
                insert_sql += insert_val

            insert_sql += ';'

            connection.execute(insert_sql)

            flash(f'{len(add_list)} students have been added to {association} for {yearterm}', 'info')

            return redirect(url_for('roster.index'))

        else:
            flash('No students selected.','danger')
            return redirect(url_for('roster.index'))

    else:
        return render_template('/roster/add.html', title = 'Add', form = form)
