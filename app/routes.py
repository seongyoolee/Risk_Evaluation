from flask import request, render_template, flash, json, redirect, url_for, Markup
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, InjuryClaimForm, InjuryClaimFilterForm
from app.tables import InjuryClaimTable
from app.models import User, Injury

import datetime
import pandas as pd
from termcolor import colored


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # login user
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        # next page after login
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, company=form.company.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/injury_claim')
def injury_claim():
    return render_template("injury_claim.html", title='Injury Claims')


def save_injury_claim(injury_claim, form):
    # Get data from form and assign it to the correct attributes of the SQLAlchemy table object
    injury_claim.injury_type = form.injury_type.data
    injury_claim.injury_cause = form.injury_cause.data
    injury_claim.open_or_closed = form.open_or_closed.data
    injury_claim.year = form.year.data
    injury_claim.incurred_loss = form.incurred_loss.data
    injury_claim.paid_loss = form.paid_loss.data
    injury_claim.description = form.description.data

    db.session.add(injury_claim)
    db.session.commit()


@app.route('/edit_injury_claim', methods=['GET', 'POST'])
def edit_injury_claim():
    form = InjuryClaimForm()
    search_form = InjuryClaimFilterForm(injury_type=['head', 'neck_spine', 'hands_arms', 'respiratory', 'feet_legs', 'torso'], injury_cause=['slips_trips_falls', 'emotional_distress', 'pet', 'chemical', 'equipment'], open_or_closed=['open', 'closed'], year_from=1951, year_to=2020, sort_by='year')

    # view table
    results = []
    qry = Injury.query.filter_by(company=current_user.company)
    if search_form.validate_on_submit():
        # sort cases
        if search_form.sort_by.data == 'injury_type':
            qry = qry.order_by(Injury.injury_type)
        elif search_form.sort_by.data == 'injury_cause':
            qry = qry.order_by(Injury.injury_cause)
        elif search_form.sort_by.data == 'open_or_closed':
            qry = qry.order_by(Injury.open_or_closed)
        elif search_form.sort_by.data == 'year':
            qry = qry.order_by(Injury.year)
        elif search_form.sort_by.data == 'incurred_loss':
            qry = qry.order_by(Injury.incurred_loss)
        elif search_form.sort_by.data == 'paid_loss':
            qry = qry.order_by(Injury.paid_loss)

        results = qry.filter(Injury.year>=search_form.year_from.data, Injury.year<=search_form.year_to.data, Injury.open_or_closed.in_(search_form.open_or_closed.data), Injury.injury_type.in_(search_form.injury_type.data), Injury.injury_cause.in_(search_form.injury_cause.data))
    else:
        # default sort by year
        results = qry.order_by(Injury.year).all()

    # check results
    if not results:
        flash('No records found.')
        return render_template('edit_injury_claim.html', title='Add/Edit Injury Claims', form=form, search_form=search_form)
    else:
        table = InjuryClaimTable(results)
        table.border = True

    if form.validate_on_submit():
        # check year
        if form.year.data < 1950 or form.year.data > datetime.datetime.now().year:
            flash('{} is not a valid year.'.format(form.year.data))
            return redirect(url_for('edit_injury_claim'))

        # check incurred loss
        if (form.incurred_loss.data * 100) % int(form.incurred_loss.data * 100) > 0:
            flash('{} is not a valid incurred loss value.'.format(form.incurred_loss.data))
            return redirect(url_for('edit_injury_claim'))

        # check paid loss
        if (form.paid_loss.data * 100) % int(form.paid_loss.data * 100) > 0:
            flash('{} is not a valid paid loss value.'.format(form.paid_loss.data))
            return redirect(url_for('edit_injury_claim'))

        # add injury claim to database
        injury_claim = Injury(company=current_user.company, injury_type=form.injury_type.data, injury_cause=form.injury_cause.data, open_or_closed=form.open_or_closed.data, year=form.year.data, incurred_loss=form.incurred_loss.data, paid_loss=form.paid_loss.data, description=form.description.data)
        save_injury_claim(injury_claim, form)
        flash('Injury claim added.')
        return redirect(url_for('edit_injury_claim'))

    return render_template('edit_injury_claim.html', title='Add/Edit Injury Claims', search_form=search_form, form=form, table=table)


@app.route('/edit_injury_claim/<int:id>', methods=['GET', 'POST'])
def edit(id):
    qry = Injury.query.filter_by(company=current_user.company).filter(Injury.id==id)
    injury_claim = qry.first()
    if injury_claim:
        form = InjuryClaimForm(formdata=request.form, obj=injury_claim)
        if request.method == 'POST' and form.validate():
            if form.submit.data:
                # save edits to db
                save_injury_claim(injury_claim, form)
                flash('Injury claim updated successfully!')
            elif form.delete.data:
                # delete from db
                db.session.delete(injury_claim)
                db.session.commit()
                flash('Injury claim deleted successfully!')
            return redirect(url_for('edit_injury_claim'))
        return render_template('edit_injury_claim.html', form=form, search_form=None, table=None)
    else:
        return 'Error loading #{id}'.format(id=id)


# @app.route('/injury_claim_graphs', methods=['GET'])
# def injury_claim_graphs():
#     injury_causes = ['head', 'neck_spine', 'hands_arms', 'respiratory', 'feet_legs', 'torso']
#     injury_causes_count = []
#     for injury_cause in injury_causes:
#         result = Injury.query.filter_by(company=current_user.company, injury_cause=injury_cause).count().all()
#         print(colored(result, 'yellow'))
#         injury_causes_count.append(result)

#     labels = ["Head","Neck & Spine","Hands & Arms","Respiratory","Feet & Legs","Torso"]
#     values = injury_causes_count
#     colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD"]
#     return render_template('injury_claim_graphs.html', title='Injury Claims Graphs', labels=json.dumps(labels), values=json.dumps(values), colors=json.dumps(colors)))


@app.route('/three_year_claim_average', methods=['GET'])
def three_year_claim_average():
    injury_claim_all = Injury.query.filter_by(company=current_user.company)
    injury_claim_losses = Injury.query.with_entities(Injury.incurred_loss, Injury.paid_loss)
    inflation_rate = 10
    incurred_avg = 0
    paid_avg = 0

    tables = []
    for i in range(0, 3):
        # injury claim table
        table = InjuryClaimTable(injury_claim_all.filter(Injury.year==datetime.datetime.now().year - (3 - i)))
        table.border = True
        tables.append(table)

        # losses for the year
        year = injury_claim_losses.filter_by(company=current_user.company, year=datetime.datetime.now().year - (3 - i)).all()
        df = pd.DataFrame(year, columns =['Incurred Loss', 'Paid Loss'])
        df['Incurred PV'] = df['Incurred Loss'] * ((1 + (inflation_rate / 100)) ** i)
        df['Paid PV'] = df['Paid Loss'] * ((1 + (inflation_rate / 100)) ** i)
        incurred_avg += df.sum(axis=0)['Incurred PV']
        paid_avg += df.sum(axis=0)['Paid PV']

    incurred_avg /= 3
    incurred_avg = str(round(incurred_avg, 2))
    paid_avg /= 3
    paid_avg = str(round(paid_avg, 2))
    
    return render_template("three_year_claim_average.html", title='3 Year Claim Average', tables=tables, inflation_rate=inflation_rate, incurred_avg=incurred_avg, paid_avg=paid_avg)