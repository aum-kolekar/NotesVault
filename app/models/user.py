from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import string
from sqlalchemy.orm import validates

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploaded_notes = db.relationship('Note', backref=db.backref('uploader', lazy=True), lazy='dynamic')
    viewed_notes = db.relationship('NoteView', backref=db.backref('viewer', lazy=True), lazy='dynamic')

    @validates('email')
    def validate_email(self, key, email):
        if not email.endswith('vit.edu'):
            raise ValueError('Only VIT email addresses are allowed')
        return email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.id}: {self.email}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 