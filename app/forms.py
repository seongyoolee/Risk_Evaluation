from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField, IntegerField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp
from app.models import User, Injury


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    company = StringField('Company', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class InjuryClaimForm(FlaskForm):
    injury_type = SelectField(u'Injury Type', validators=[DataRequired()], 
        choices=[('head', 'Head'), ('neck_spine', 'Neck & Spine'), ('hands_arms', 'Hands & Arms'), ('respiratory', 'Respiratory'), ('feet_legs', 'Feet & Legs'), ('torso', 'Torso')])
    injury_cause = SelectField(u'Injury Cause', validators=[DataRequired()], 
        choices=[('slips_trips_falls', 'Slips, Trips, Falls'), ('emotional_distress', 'Emotional Distress'), ('pet', 'Pet Related'), ('chemical', 'Chemical'), ('equipment', 'Equipment')])
    open_or_closed = SelectField(u'Open/Closed', validators=[DataRequired()], 
        choices=[('open', 'Open'), ('closed', 'Closed')])
    year = IntegerField('Year', validators=[DataRequired()])
    incurred_loss = FloatField('Incurred Loss', validators=[DataRequired()])
    paid_loss = FloatField('Paid Loss', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class InjuryClaimFilterForm(FlaskForm):
    injury_type = SelectMultipleField(u'Injury Type', 
        choices=[('head', 'Head'), ('neck_spine', 'Neck & Spine'), ('hands_arms', 'Hands & Arms'), ('respiratory', 'Respiratory'), ('feet_legs', 'Feet & Legs'), ('torso', 'Torso')])
    injury_cause = SelectMultipleField(u'Injury Cause', 
        choices=[('slips_trips_falls', 'Slips, Trips, Falls'), ('emotional_distress', 'Emotional Distress'), ('pet', 'Pet Related'), ('chemical', 'Chemical'), ('equipment', 'Equipment')])
    open_or_closed = SelectField(u'Open/Closed', 
        choices=[('open', 'Open'), ('closed', 'Closed')])
    year_from = IntegerField('Year From')
    year_to = IntegerField('Year To')
    search = SubmitField('Search')