from flask_login import UserMixin
from myapp import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Transcript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    ipfs_hash = db.Column(db.String(120), nullable=False)
    student = db.relationship("User", backref=db.backref("transcripts", lazy=True))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
