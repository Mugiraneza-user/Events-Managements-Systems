from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from datetime import datetime

admin = Blueprint('admin', __name__)

@admin.before_request
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin.route('/')
@login_required
def dashboard():
    now = datetime.now()
    events_count = Event.query.count()
    users_count = User.query.count()
    registrations_count = Registration.query.count()
    upcoming_events = Event.query.filter(Event.start_date > datetime.utcnow()).count()
    
    return render_template('admin/dashboard.html', now=now,
                           title='Admin Dashboard',
                           events_count=events_count,
                           users_count=users_count,
                           registrations_count=registrations_count,
                           upcoming_events=upcoming_events)

@admin.route('/events')
@login_required
def events():
    now = datetime.now()
    events_list = Event.query.order_by(Event.start_date).all()
    return render_template('admin/events.html', title='Manage Events',now=datetime.now(), events=events_list)

@admin.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    now = datetime.now()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
        capacity = int(request.form['capacity'])
        image_url = request.form['image_url']
        
        if start_date >= end_date:
            flash('End date must be after start date', 'danger')
            return redirect(url_for('admin.create_event'))
        
        event = Event(title=title, description=description, location=location,
                     start_date=start_date, end_date=end_date, capacity=capacity, 
                     image_url=image_url)
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin.events'))
    
    return render_template('admin/event_form.html',now=now, title='Create Event')

@admin.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    now = datetime.now()
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        event.location = request.form['location']
        event.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        event.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
        event.capacity = int(request.form['capacity'])
        event.image_url = request.form['image_url']
        
        if event.start_date >= event.end_date:
            flash('End date must be after start date', 'danger')
            return redirect(url_for('admin.edit_event', event_id=event_id))
        
        db.session.commit()
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin.events'))
    
    start_date = event.start_date.strftime('%Y-%m-%dT%H:%M')
    end_date = event.end_date.strftime('%Y-%m-%dT%H:%M')
    
    return render_template('admin/event_form.html',now=now, title='Edit Event', 
                          event=event, start_date=start_date, end_date=end_date)

@admin.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Delete all registrations for this event
    Registration.query.filter_by(event_id=event_id).delete()
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('admin.events'))

@admin.route('/users')
@login_required
def users():
    now = datetime.now()
    users_list = User.query.order_by(User.created_at).all()
    return render_template('admin/users.html',now=now, title='Manage Users', users=users_list)

@admin.route('/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow removing admin status from the current user
    if user.id == current_user.id:
        flash('You cannot change your own admin status', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin status {status} for {user.username}', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting the current user
    if user.id == current_user.id:
        flash('You cannot delete your own account while logged in', 'danger')
        return redirect(url_for('admin.users'))
    
    # Delete all registrations for this user
    Registration.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} deleted successfully', 'success')
    return redirect(url_for('admin.users'))
@admin.route('/events/<int:event_id>/registrations')
@login_required
def event_registrations(event_id):
    now = datetime.now()
    event = Event.query.get_or_404(event_id)
    
    # Get all registrations for this event with their associated users
    registrations = Registration.query.filter_by(event_id=event_id).all()
    
    # Get user details for each registration
    registrants = []
    for registration in registrations:
        user = User.query.get(registration.user_id)
        registrants.append({
            'registration': registration,
            'user': user
        })
    return render_template('admin/event_registrations.html', 
                          now=now,
                          title=f'Registrations for {event.title}',
                          event=event,
                          registrants=registrants,
                          registered_count=len(registrants))

@admin.route('/registrations')
@login_required
def registrations():
    now = datetime.now()
    events_list = Event.query.order_by(Event.start_date).all()
    
    # Get registration counts for each event
    event_registration_data = []
    for event in events_list:
        registration_count = Registration.query.filter_by(event_id=event.id).count()
        capacity_percentage = (registration_count / event.capacity * 100) if event.capacity > 0 else 0
        
        event_registration_data.append({
            'event': event,
            'registration_count': registration_count,
            'capacity_percentage': capacity_percentage
        })
    
    return render_template('admin/registrations.html', 
                          now=now,
                          title='Event Registrations',
                          event_registration_data=event_registration_data)

@admin.route('/registrations/<int:registration_id>/delete', methods=['POST'])
@login_required
def delete_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    event_id = registration.event_id
    
    # Get user info before deleting for flash message
    user = User.query.get(registration.user_id)
    event = Event.query.get(event_id)
    
    db.session.delete(registration)
    db.session.commit()
    
    flash(f'Registration for {user.username} to {event.title} has been deleted', 'success')
    return redirect(url_for('admin.event_registrations', event_id=event_id))