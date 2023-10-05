from app import app
from flask import render_template, request
from models import User, Course, UserCourse, Prerequisite, Corequisite, db
from datetime import datetime
import enum

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/level', methods=['GET', 'POST'])
def level():
    if request.method == 'POST':
        session_id = request.form['session_id']
        level = request.form['level']
        cgpa = request.form['cgpa']
        user = User(session_id=session_id, level=level, cgpa=cgpa)
        db.session.add(user)
        db.session.commit()
        return render_template('level.html', session_id=session_id, level=level, cgpa=cgpa)
    else:
        return render_template('level.html')