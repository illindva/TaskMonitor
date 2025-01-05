from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Authorizations(db.Model):
    __tablename__ = 'Authorizations'
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    encryption_flag = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Authorization {self.username}>"

class SchTasks(db.Model):
    __tablename__ = 'SchTasks'
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)
    call_this = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)  # Includes timezone
    end_time = db.Column(db.DateTime, nullable=False)  # Includes timezone
    orig_start_time = db.Column(db.DateTime, nullable=False)  # Same as start_time initially
    orig_end_time = db.Column(db.DateTime, nullable=False)  # Same as end_time initially
    is_completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, default=None, onupdate=datetime.utcnow)
    day_frequency = db.Column(db.String(255), nullable=False)  # Comma-separated days, e.g., "Monday,Tuesday"

    def __repr__(self):
        return f"<Task {self.task_name}>"


