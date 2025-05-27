from app import db
from datetime import datetime

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(1024))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    registrations = db.relationship('Registration', backref='event', lazy='dynamic')
    
    def __repr__(self):
        return f'<Event {self.title}>'
    
    @property
    def registered_count(self):
        return self.registrations.count()
    
    @property
    def available_seats(self):
        return self.capacity - self.registered_count
    
    @property
    def is_full(self):
        return self.available_seats <= 0
    
    @property
    def is_upcoming(self):
        return self.start_date > datetime.utcnow()