from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError



class Roster(FlaskForm):       
    yearterm = SelectField ('Year.Term', 
                        choices=[], validators=[DataRequired()])
    association = SelectField ('Association', choices=[], 
                                default = None, validators=[DataRequired()])
    view_roster = SubmitField("View Roster")
    delete = BooleanField("Delete")
    add_students = SubmitField("Add Students")
    delete_students = SubmitField("Delete Students")
    save_roster = SubmitField("Save as .csv")
    new_search = SubmitField("New Search")


class AddStudent(FlaskForm):
    students = SelectMultipleField('Student Names', choices = [], default = (None, 'Please Select Students'), validators=[])
    submit = SubmitField('Add Students')
    cancel = SubmitField('Cancel')


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


@bp.route("/roster/index", methods = ['GET', 'POST'])
#@login_required #Forces user to login to navigate to roster page.
def index():

    form = Roster()
    form.yearterm.choices = session.get('yearterm_list')
    form.association.choices = session.get('association_list')

    if form.validate_on_submit():
        yearterm = form.yearterm.data
        session['yearterm'] = yearterm
        year = yearterm.split('.')[0]
        term = yearterm.split('.')[1]
        association = form.association.data
        session['association'] = association

        print(request.form)

        if 'new_search' in request.form:
            return redirect(url_for("roster.index"))

        elif 'add_students' in request.form:
            flash("Add Students", "info")
            return render_template("roster/add.html", form=AddStudent(), association=association, yearterm=yearterm )

        elif 'delete_students' in request.form:

            del_list = request.form.getlist('delete_student')
            print(del_list)
            if (del_list):
                sql_str = ""
                for id in del_list:
                    sql_str += f"""
                    DELETE 
                    FROM ASSOCIATION 
                    WHERE PEOPLE_ORG_CODE_ID = '{id}' 
                    AND ASSOCIATION = '{association}' 
                    AND ACADEMIC_TERM = '{term}' 
                    AND ACADEMIC_YEAR = '{year}' ;
                    """

                #connection.execute(sql_str)
                print(sql_str)
                flash(f"{len(del_list)} have been deleted from {association} for {term} {year}.", "danger")
                flash(f"Delete Students: {del_list}", "warn")

                # refresh roster
                df_export = association_export(year, term, association, connection)
                if not(df_export.empty):
                    df_export = df_export.rename(columns={'PEOPLE_ORG_CODE_ID': 'PSC_ID'})
                    result = df_export.to_dict('split')['data']
                else:
                    flash("No results were returned. Please try again.")
                    return render_template('roster/index.html', title='Roster', form=form)
                
                return render_template('roster/index.html',
                    form = form,
                    association = association,
                    yearterm = yearterm,
                    title = f"{association} - {term} {year}", 
                    result = result,
                    resultlength = f"{str(len(result))} result(s) found."
                    )

            else:
                flash(f"No students selected for deletion.","warn")

        
        df_export = association_export(year, term, association, connection)

        if not(df_export.empty):
            df_export = df_export.rename(columns={'PEOPLE_ORG_CODE_ID': 'PSC_ID'})
            result = df_export.to_dict('split')['data']

            if 'save_roster' in request.form:
                today_str = datetime.now().strftime("%Y%m%d")
                filename = f"{year}{term}_{association}_Roster_{today_str}.csv"
                resp = make_response(df_export.to_csv(index=False))
                resp.headers["Content-Disposition"] = ( f"attachment; filename={filename}" )
                resp.headers["content-Type"] = "text/csv"
                return resp

            else: # 'view_roster' in request.form:
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
            return render_template('roster/index.html', title='Roster', form=form)

        flash("Error: Button not known.", "error")
        return render_template('roster/index.html', title='Roster', form=form)
       
    else:
        return render_template('roster/index.html', title='Roster', form=form)


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




from flask import render_template, url_for, flash, redirect, Blueprint
#from assoc_mgr.add.forms import AddStudentForm
from assoc_mgr.queries import students, associations, yearterms, association_members
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import pandas as pd



@bp.route("/roster/add", methods =['GET', 'POST'])
#@login_required #Forces user to login to navigate to update page.
def add(yearterm=None, association=None):

    form = AddStudent()

    today = datetime.now()
    now = str(today.year)
    one_year_ago = str(today.year - 1)
    df_student = students(now, one_year_ago, connection)
    student_list = [tuple(s) for s in df_student[['PEOPLE_CODE_ID', 'STUDENT']].to_numpy()]

    form.students.choices = student_list

    if not yearterm:
        yearterm = session.get('yearterm')

    if not association:
        association = session.get('association')

    if form.validate_on_submit():

        year = yearterm.split('.')[0]
        term = yearterm.split('.')[1]

        print('ADD function', request.form)
        if 'cancel' in request.form:
            redirect(url_for('roster.index', ), )

        assoc_members = association_members(year, term, association, connection)

        add_list = form.student.data

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

            print(insert_sql)
            connection.execute(insert_sql)

            flash(f'{len(add_list)} students have been added to {association} for {yearterm}', 'info')

            return redirect(url_for('roster.index'), )

        else:
            flash('No students selected.','danger')
            return redirect(url_for('roster.index'))

    else:
        return render_template('/roster/index.html', form = form)
