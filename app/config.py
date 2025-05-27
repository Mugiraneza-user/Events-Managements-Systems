import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:Mugiraneza@123@localhost/event_managements'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Mugiraneza%40123@localhost/event_managements'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
