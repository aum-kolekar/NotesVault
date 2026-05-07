from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.note import Note
from app.models.note_view import NoteView
from werkzeug.security import generate_password_hash
import re
from datetime import datetime
from flask import current_app

bp = Blueprint('auth', __name__)

def is_valid_college_email(email):
    return email.endswith('@vit.edu')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        college = request.form.get('college')
        department = request.form.get('department')

        # Validate email
        if not email.endswith('@vit.edu'):
            flash('Only VIT email addresses are allowed.', 'error')
            return render_template('auth/register.html')

        # Check existing user
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')

        try:
            # Create user
            user = User(
                email=email,
                name=name,
                college=college,
                department=department
            )

            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            print(e)
            flash('Registration failed.', 'error')

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html')
        
        # If everything is okay, log in the user
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))
    
    return render_template('auth/login.html')

@bp.route('/logout')

def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/profile')

def profile():
    return render_template('auth/profile.html', Note=Note, NoteView=NoteView)

@bp.route('/profile/edit', methods=['GET', 'POST'])

def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        college = request.form.get('college')
        department = request.form.get('department')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Update basic info
        current_user.name = name
        current_user.college = college
        current_user.department = department

        # Update password if provided
        if current_password and new_password and confirm_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('auth/edit_profile.html')
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return render_template('auth/edit_profile.html')
            
            current_user.set_password(new_password)
            flash('Password updated successfully.', 'success')

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/edit_profile.html')