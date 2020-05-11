from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response, session, redirect
#from flask_login import login_user, current_user, logout_user, login_required
#from assoc_mgr.auth import login_required
#from assoc_mgr.db import get_db
from assoc_mgr.roster.forms import Roster, AddStudent
from assoc_mgr.queries import students, associations, yearterms, association_export, association_members
from datetime import datetime
import pandas as pd
from loguru import logger


bp = Blueprint('roster', __name__)


from assoc_mgr import connection as assoc_mgr_conn
connection = assoc_mgr_conn


@bp.route("/roster/index", methods = ['GET', 'POST'])
#@login_required #Forces user to login to navigate to roster page.
def index():

    form = Roster()
    form.yearterm.choices = session.get('yearterm_list')
    form.association.choices = session.get('association_list')

    if "yearterm" in request.args:
        yearterm = request.args['yearterm']
        form.yearterm.data = yearterm
    else:
        yearterm = None
    if "association" in request.args:
        association = request.args['association']
        form.association.data = association
    else:
        association = None


    if form.validate_on_submit():
        yearterm = form.yearterm.data
        session['yearterm'] = yearterm
        year = yearterm.split('.')[0]
        term = yearterm.split('.')[1]
        association = form.association.data
        session['association'] = association

        if 'new_search' in request.form:
            return redirect(url_for("roster.index"))

        elif 'add_students' in request.form:
            return redirect(url_for('roster.add', association=association, yearterm=yearterm))

        elif 'delete_students' in request.form:

            del_list = request.form.getlist('delete_student')
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

                connection.execute(sql_str)
                logger.info(f"{del_list} have been deleted from {association} for {term} {year}.")
                flash(f"{del_list} have been deleted from {association} for {term} {year}.", "info")
                
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
                logger.info(f"Roster for {association}-{term} {year} exported.")
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
        return render_template('roster/index.html', form=form, yearterm=yearterm, association=association)



@bp.route("/roster/add", methods =['GET', 'POST'])
#@login_required #Forces user to login to navigate to update page.
def add():

    form = AddStudent()

    today = datetime.now()
    now = str(today.year)
    one_year_ago = str(today.year - 1)
    df_student = students(now, one_year_ago, connection)
    student_list = [tuple(s) for s in df_student[['PEOPLE_CODE_ID', 'STUDENT']].to_numpy()]

    form.students.choices = student_list

    if "yearterm" in request.args:
        yearterm = request.args['yearterm']
    if "association" in request.args:
        association = request.args['association']
    

    if form.validate_on_submit():

        year = yearterm.split('.')[0]
        term = yearterm.split('.')[1]

        if 'cancel' in request.form:
#            return render_template('roster/index.html', title='Roster', form=Roster(), yearterm=yearterm, association=association)
            return redirect(url_for('roster.index', association=association, yearterm=yearterm))

        assoc_members = association_members(year, term, association, connection)

        add_list = form.students.data

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

            logger.info(f"{add_list} have been added to {association} for {term} {year}.")
            flash(f'{add_list} have been added to {association} for {yearterm}', 'info')
            return redirect(url_for('roster.index', association=association, yearterm=yearterm))

        else:
            flash('No students selected.','danger')
            return redirect(url_for('roster.index'))

    else:
        return render_template('/roster/add.html', form = form, yearterm=yearterm, association=association)
