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
        if 'session_id' not in session or User.query.get(session['session_id']) is None:
            flash('You must select a level first')
            return redirect(url_for('level_get'))
        return func(*args, **kwargs)
    return inner


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/level', methods=['GET'])
def level_get():
    level = Level.FOUNDATION.value
    if 'session_id' in session:
        user = User.query.get(session['session_id'])
        if user:
            level = user.level.value
    return render_template('level.html', level=level)

@app.route('/level', methods=['POST'])
def level_post():
    try:
        level = Level(int(request.form['level']))
    except:
        flash('Invalid level ' + request.form['level'])
        return redirect(url_for('level_get'))
    if 'session_id' in session:
        user = User.query.get(session['session_id'])
        if not user:
            user = User(session_id=session['session_id'], level=level)
            db.session.add(user)
        else:
            user.level = level
    else:
        session_id = str(uuid4())
        while User.query.get(session_id) is not None:
            session_id = str(uuid4())
        session['session_id'] = session_id
        user = User(session_id=session_id, level=level)
        db.session.add(user)
    db.session.commit()
    return redirect(url_for('courses', session_id=session_id))


@app.route('/courses', methods=['GET'])
@auth_required
def courses_get():
    user = User.query.get(session['session_id'])
    user_courses = user.user_courses
    courses = []
    for level in range(Level.FOUNDATION.value, user.level.value + 1):
        courses.extend(Course.query.filter_by(course_level=Level(level)).all())
    return render_template('courses.html', courses=courses, user_courses=user_courses, level=user.level, cgpa=user.cgpa)

@app.route('/courses', methods=['POST'])
@auth_required
def courses_post():
    user = User.query.get(session['session_id'])
    for course_code in request.form:
        if course_code == 'csrf_token':
            continue
        for c in Course.get(course_code).course_prereq:
            if c.prereq_code not in request.form:
                flash('You have not met the prerequisites for ' + course_code)
                return redirect(url_for('courses_get'))
        for c in Course.get(course_code).course_coreq:
            if c.coreq_code not in request.form:
                flash('You have not met the corequisites for ' + course_code)
                return redirect(url_for('courses_get'))
        try:
            grade = Grade(int(request.form[course_code]))
        except:
            flash('Invalid grade for ' + course_code)
            return redirect(url_for('courses_get'))
        user_course = UserCourse.query.filter_by(session_id=session['session_id'], course_code=course_code).first()
        if user_course:
            user_course.grade = grade
        else:
            user_course = UserCourse(session_id=session['session_id'], course_code=course_code, grade=grade)
            db.session.add(user_course)
    db.session.commit()
    user.calculate_cgpa()
    return redirect(url_for('cgpa_get'))

@app.route('/cgpa', methods=['GET'])
@auth_required
def cgpa_get():
    user = User.query.get(session['session_id'])
    if not user.cgpa:
        flash('You have not completed any courses')
        return redirect(url_for('courses_get'))
    return render_template('cgpa.html', cgpa=user.cgpa)

@app.route('/forgetme', methods=['GET'])
def forgetme():
    if 'session_id' in session:
        session.pop('session_id', None)
    return redirect(url_for('index'))