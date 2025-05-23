from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                flash('Please check your email and try again.')
                current_app.logger.info(f'Failed login attempt for non-existent email: {email}')
                return render_template('auth/login.html')
            
            if not user.check_password(password):
                flash('Please check your password and try again.')
                current_app.logger.info(f'Failed login attempt for user: {email}')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            current_app.logger.info(f'Successful login for user: {email}')
            
            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            return redirect(url_for('main.profile'))
            
        except Exception as e:
            current_app.logger.error(f'Login error: {str(e)}')
            flash('An error occurred. Please try again.')
            return render_template('auth/login.html')

    return render_template('auth/login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email address already exists')
                return redirect(url_for('auth.signup'))

            new_user = User(email=email, username=username)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('auth.login'))
        except Exception as e:
            current_app.logger.error(f'Signup error: {str(e)}')
            flash('An error occurred during signup. Please try again.')
            return render_template('auth/signup.html')

    return render_template('auth/signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 