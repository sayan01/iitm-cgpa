from app import app
from flask import render_template, request, redirect, url_for, session, flash
from models import User, Course, UserCourse, Prerequisite, Corequisite, db, Level, Grade
from datetime import datetime
import enum
from uuid import uuid4
from functools import wraps


# decorator for auth
def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'session_id' not in session or User.get(session['session_id']) is None:
            flash('You must select a level first')
            return redirect(url_for('level_get'))
        return func(*args, **kwargs)
    return inner


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/level', methods=['GET'])
def level_get():
    level = Level.FOUNDATION.value
    if 'session_id' in session:
        user = User.get(session['session_id'])
        if user:
            level = user.level.value
    return render_template('level.html', level=level)

@app.route('/level', methods=['POST'])
def level_post():
    try:
        level = Level(int(request.form['level']))
    except:
        flash('Invalid level')
        return redirect(url_for('level_get'))
    if 'session_id' in session:
        user = User.get(session['session_id'])
        if not user:
            user = User(session_id=session['session_id'], level=level)
            db.session.add(user)
        else:
            user.level = level
    else:
        session_id = str(uuid4())
        while User.get(session_id) is not None:
            session_id = str(uuid4())
        session['session_id'] = session_id
        user = User(session_id=session_id, level=level)
        db.session.add(user)
    db.session.commit()
    return redirect(url_for('courses', session_id=session_id))


@app.route('/courses', methods=['GET'])
@auth_required
def courses_get():
    user = User.get(session['session_id'])
    user_courses = user.user_courses
    courses = []
    for level in range(Level.FOUNDATION.value, user.level.value + 1):
        courses.extend(Course.query.filter_by(course_level=Level(level)).all())
    return render_template('courses.html', courses=courses, user_courses=user_courses, level=user.level, cgpa=user.cgpa)

@app.route('/courses', methods=['POST'])
@auth_required
def courses_post():
    user = User.get(session['session_id'])
    user_courses = user.user_courses
    for user_course in user_courses:
        db.session.delete(user_course)
    for course_code in request.form:
        if course_code == 'csrf_token':
            continue
        grade = Grade(int(request.form[course_code]))
        user_course = UserCourse(session_id=session['session_id'], course_code=course_code, grade=grade)
        db.session.add(user_course)
    db.session.commit()
    user.calculate_cgpa()
    return redirect(url_for('courses_get'))

@app.route('/forgetme', methods=['GET'])
def forgetme():
    if 'session_id' in session:
        session.pop('session_id', None)
    return redirect(url_for('index'))