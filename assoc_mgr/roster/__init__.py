from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError



class Roster(FlaskForm):       
    yearterm = SelectField ('Year.Term', 
                        choices=[], validators=[DataRequired()])
    association = SelectField ('Association', choices=[], 
                                default = None, validators=[DataRequired()])
    submit = SubmitField("View Roster")


class Export(FlaskForm):
    yearterm = SelectField ('Year.Term', 
                        choices=[], validators=[DataRequired()])
    association = SelectField ('Association', choices=[], 
                                default = None, validators=[DataRequired()])
    submit = SubmitField("DOWNLOAD")


from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response
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

df_yearterm = yearterms(connection)
df_association = associations(connection)


@bp.route("/roster", methods = ['GET', 'POST'])
#@login_required #Forces user to login to navigate to roster page.
def roster():

    form = Roster()
    form.yearterm.choices = [tuple(t) for t in df_yearterm[['YEARTERM', 'YEARTERM']].to_numpy()]
    form.association.choices = [tuple(a) for a in df_association.to_numpy()]

    if form.validate_on_submit():
        yearterm = form.yearterm.data
        year = df_yearterm.loc[(df_yearterm['YEARTERM'] == yearterm),'ACADEMIC_YEAR'].iloc[0]
        term = df_yearterm.loc[(df_yearterm['YEARTERM'] == yearterm),'ACADEMIC_TERM'].iloc[0]
        association = form.association.data

        df_export = association_export(year, term, association, connection)
        df_export = df_export.rename(columns={'PEOPLE_ORG_CODE_ID': 'PSC_ID'})

        if not(df_export.empty):
            result = df_export.to_dict('split')['data']
            return render_template('roster/display.html', 
                association = f"{association}",
                yearterm = f"{yearterm}",
                title = f"{association} - {term} {year}", 
                result = result,
                resultlength = f"{str(len(result))} result(s) found."
                )

        else:
            flash("No results were returned. Please Try again.")
            return render_template('roster/roster.html', title = 'Retrieve Roster', form = form)
    else:
        return render_template('roster/roster.html', title = 'Retrieve Roster', form = form)


#Handler for Delete Request
@bp.route("/roster/display", methods = ['GET', 'POST'])
#@login_required 
def rosterdisplay():

    pscid = request.args.get('pscid')
    lname = request.args.get('lname')
    fname = request.args.get('fname')
    association = request.args.get('association')
    term = request.args.get('term')
    year = request.args.get('year')
 
    if request.method == 'GET':
        sql_str = f"""
        DELETE 
        FROM ASSOCIATION 
        WHERE PEOPLE_ORG_CODE_ID = '{pscid}' 
          AND ASSOCIATION = '{association}' 
          AND ACADEMIC_TERM = '{term}' 
          AND ACADEMIC_YEAR = '{year}' 
        """

        connection.execute(sql_str)

        flash(f"{lname}, {fname} has been deleted from {association} for {term} {year}.", "danger")

    return redirect(url_for('roster.index'))


@bp.route("/roster/export", methods = ['GET', 'POST'])
#@login_required
def rosterexport():
    
    yearterm = request.args.get('yearterm')
    association = request.args.get('association')

    form = Export(yearterm=yearterm, association=association )

    form.yearterm.choices = [tuple(t) for t in df_yearterm[['YEARTERM', 'YEARTERM']].to_numpy()]
    form.association.choices = [tuple(a) for a in df_association.to_numpy()]

    if form.validate_on_submit():
        yearterm = form.yearterm.data
        year = df_yearterm.loc[(df_yearterm['YEARTERM'] == yearterm),'ACADEMIC_YEAR'].iloc[0]
        term = df_yearterm.loc[(df_yearterm['YEARTERM'] == yearterm),'ACADEMIC_TERM'].iloc[0]
        association = form.association.data

        df_export = association_export(year, term, association, connection)

        if not(df_export.empty):
            df_export = df_export.rename(columns={'PEOPLE_ORG_CODE_ID': 'PSC_ID'})
            resp = make_response(df_export.to_csv(index=False))
            resp.headers["Content-Disposition"] = ( f"attachment; filename={year}{term}_{association}_Roster_{today_str}.csv" )
            resp.headers["content-Type"] = "text/csv"
            return resp

        else:
            flash("No results were returned. Please Try again.")
 
    return render_template('roster/export.html', title = 'Export Roster', form = form, yearterm=yearterm, association=association)

    