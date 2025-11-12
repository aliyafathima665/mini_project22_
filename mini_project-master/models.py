from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    usn = db.Column(db.String(20), unique=True, nullable=False)
    mobile = db.Column(db.String(15))
    lives_in = db.Column(db.String(50))  # e.g., 'hostel', 'home', 'pg'
    address = db.Column(db.Text)
    health_concerns = db.Column(db.Text)
    ptm_record = db.Column(db.Text, default='[]')  # JSON: [{'date': 'YYYY-MM-DD', 'time': 'HH:MM', 'guardian': 'Name', 'discussion': 'Text'}]
    call_record = db.Column(db.Text, default='[]')  # JSON: [{'date': 'YYYY-MM-DD', 'reason': 'Text'}]
    results = db.Column(db.Text, default='{}')  # JSON: {'1': {'sgpa': 8.5, 'backlogs': 0}, ...}
    parents_name = db.Column(db.String(100))
    parents_contact = db.Column(db.String(15))
    skills = db.Column(db.Text, default='[]')  # JSON: ['Cert1', 'Project2']
    extra_curricular = db.Column(db.Text, default='[]')  # JSON: ['Sports', 'Hackathon']
    semester = db.Column(db.Integer)
    passed_out_year = db.Column(db.Integer)  # Null if not passed out
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Student {self.usn}>'

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(120), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Faculty {self.email}>'