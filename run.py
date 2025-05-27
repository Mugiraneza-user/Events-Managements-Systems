from app import create_app, db
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Event': Event, 
        'Registration': Registration
    }

if __name__ == '__main__':
    app.run(debug=True)