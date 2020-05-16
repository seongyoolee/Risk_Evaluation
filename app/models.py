from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    company = db.Column(db.String(50), index=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {} from {}>'.format(self.username, self.company)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Injury(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(50), index=True)
    injury_type = db.Column(db.String(30), index=True)
    injury_cause = db.Column(db.String(30), index=True)
    open_or_closed = db.Column(db.String(1), index=True)
    year = db.Column(db.Integer)
    incurred_loss = db.Column(db.Float)
    paid_loss = db.Column(db.Float)
    description = db.Column(db.String(100))
