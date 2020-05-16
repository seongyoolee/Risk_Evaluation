from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from flask import request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, InjuryClaimForm, InjuryClaimFilterForm
from app.tables import InjuryClaimTable
from app.models import User, Injury

import datetime
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
    search_form = InjuryClaimFilterForm(injury_type=['head', 'neck_spine', 'hands_arms', 'respiratory', 'feet_legs', 'torso'], injury_cause=['slips_trips_falls', 'emotional_distress', 'pet', 'chemical', 'equipment'], open_or_closed='open', year_from=1951, year_to=2020)

    # view table
    results = []
    qry = Injury.query.filter_by(company=current_user.company)
    if search_form.validate_on_submit():
        results = qry.filter(Injury.year>=search_form.year_from.data, Injury.year<=search_form.year_to.data, Injury.open_or_closed==search_form.open_or_closed.data, Injury.injury_type.in_(search_form.injury_type.data), Injury.injury_cause.in_(search_form.injury_cause.data))
    else:
        results = qry.all()

    # check 
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
            # save edits to db
            save_injury_claim(injury_claim, form)
            flash('Injury claim updated successfully!')
            return redirect(url_for('edit_injury_claim'))
        return render_template('edit_injury_claim.html', form=form)
    else:
        return 'Error loading #{id}'.format(id=id)
