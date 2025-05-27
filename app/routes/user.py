from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.registration import Registration
from werkzeug.security import check_password_hash

user = Blueprint('user', __name__)

@user.route('/profile')
@login_required
def profile():
    now = datetime.now()
    registrations = Registration.query.filter_by(user_id=current_user.id).order_by(Registration.registration_date.desc()).all()
    return render_template('user/profile.html',now=now, title='My Profile', registrations=registrations)

@user.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    full_name = request.form['full_name']
    email = request.form['email']
    
    # Check if email is already taken by another user
    if email != current_user.email and User.query.filter_by(email=email).first():
        flash('Email already in use', 'danger')
        return redirect(url_for('user.profile'))
    
    current_user.full_name = full_name
    current_user.email = email
    
    db.session.commit()
    flash('Profile updated successfully', 'success')
    return redirect(url_for('user.profile'))

@user.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    if not check_password_hash(current_user.password_hash, current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('user.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('user.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Password changed successfully', 'success')
    return redirect(url_for('user.profile'))