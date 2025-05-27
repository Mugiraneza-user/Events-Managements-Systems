from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.event import Event
from app.models.registration import Registration
from datetime import datetime

events = Blueprint('events', __name__)

@events.route('/')
def index():
    now = datetime.utcnow() 
    page = request.args.get('page', 1, type=int)
    upcoming_events = Event.query.filter(Event.start_date > datetime.utcnow()).order_by(Event.start_date).paginate(page=page, per_page=6)
    past_events = Event.query.filter(Event.start_date <= datetime.utcnow()).order_by(Event.start_date.desc()).limit(3).all()
     
    return render_template('events/index.html', title='Events', now=now,
                          upcoming_events=upcoming_events, past_events=past_events)

@events.route('/<int:event_id>')
def details(event_id):
    now = datetime.now()
    event = Event.query.get_or_404(event_id)
    
    user_registered = False
    if current_user.is_authenticated:
        registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        user_registered = registration is not None
    
    return render_template('events/details.html',now=now ,title=event.title, 
                          event=event, user_registered=user_registered)

@events.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if user is already registered
    existing_registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing_registration:
        flash('You are already registered for this event', 'info')
        return redirect(url_for('events.details', event_id=event_id))
    
    # Check if event is full
    if event.is_full:
        flash('Sorry, this event is already at full capacity', 'danger')
        return redirect(url_for('events.details', event_id=event_id))
    
    # Check if event is in the past
    if event.start_date <= datetime.utcnow():
        flash('Cannot register for past events', 'danger')
        return redirect(url_for('events.details', event_id=event_id))
    
    # Create registration
    registration = Registration(user_id=current_user.id, event_id=event_id)
    db.session.add(registration)
    db.session.commit()
    
    flash('Successfully registered for the event!', 'success')
    return redirect(url_for('events.details', event_id=event_id))

@events.route('/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_registration(event_id):
    registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if not registration:
        flash('You are not registered for this event', 'danger')
        return redirect(url_for('events.details', event_id=event_id))
    
    db.session.delete(registration)
    db.session.commit()
    
    flash('Registration cancelled successfully', 'success')
    return redirect(url_for('events.details', event_id=event_id))