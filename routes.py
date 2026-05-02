"""
Routes for the application.
"""
from app import app
from flask import render_template, request, redirect, url_for, session, flash
from models import User, Course, UserCourse, db, Level, Grade
from uuid import uuid4
from functools import wraps


def auth_required(func):
    """
    Decorator to guard authenticated routes using flask session.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        if 'session_id' not in session or User.query.get(session['session_id']) is None:
            flash('You must select a level first')
            return redirect(url_for('level_get'))
        return func(*args, **kwargs)
    return inner


@app.route('/')
def index():
    """
    Route for landing banner CTA.
    """
    return render_template('index.html')

@app.route('/about')
def about():
    """
    Route for about page and data collection policy.
    """
    return render_template('about.html')

@app.route('/donate')
def donate():
    """
    Route for the donate page.
    """
    return render_template('donate.html')

@app.route('/level', methods=['GET'])
def level_get():
    """
    Route for level selection page.
        - If the user has already selected a level, it is shown as selected.
    """
    level = Level.FOUNDATION
    if 'session_id' in session:
        user = User.query.get(session['session_id'])
        if user:
            level = user.level
    levels = Level.__members__.values()
    return render_template('level.html', levels=levels, level=level)

@app.route('/level', methods=['POST'])
def level_post():
    """
    Route for handling level selection POST requests.
    """
    try:
        level = Level(int(request.form['level']))
    except ValueError:
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
    return redirect(url_for('courses_get'))


@app.route('/courses', methods=['GET'])
@auth_required
def courses_get():
    """
    Route for course selection page.
    """
    user = User.query.get(session['session_id'])
    user_courses = user.user_courses
    user_courses = {
        c.course_code: c.grade.value for c in user_courses
    }
    courses = []
    for level in range(Level.FOUNDATION.value, user.level.value + 1):
        courses.extend(Course.query.filter_by(course_level=Level(level)).all())
    grades = Grade.__members__.values()
    return render_template(
        'courses.html',
        courses=courses,
        user_courses=user_courses,
        level=user.level,
        grades=grades
    )

@app.route('/courses', methods=['POST'])
@auth_required
def courses_post():
    """
    Route for handling course selection POST requests.
    """
    user = User.query.get(session['session_id'])
    invalid = False
    for course_code in request.form:
        if course_code == 'csrf_token':
            continue
        if not Course.query.get(course_code):
            flash('Invalid course ' + course_code)
            invalid = True
        if request.form[course_code] == '0':
            if UserCourse.query.filter_by(session_id=session['session_id'], course_code=course_code).first():
                db.session.delete(UserCourse.query.filter_by(session_id=session['session_id'], course_code=course_code).first())
            continue
        try:
            grade = Grade(int(request.form[course_code]))
        except ValueError:
            flash('Invalid grade for ' + course_code)
            invalid = True
        user_course = UserCourse.query.filter_by(session_id=session['session_id'], course_code=course_code).first()
        if user_course:
            user_course.grade = grade
        else:
            user_course = UserCourse(session_id=session['session_id'], course_code=course_code, grade=grade)
            db.session.add(user_course)
    db.session.commit()
    if invalid:
        return redirect(url_for('courses_get'))
    user.calculate_cgpa()
    user.calculate_project_cgpa()
    return redirect(url_for('cgpa_get'))

@app.route('/cgpa', methods=['GET'])
@auth_required
def cgpa_get():
    """
    Route for displaying CGPA information.
    """
    user = User.query.get(session['session_id'])
    if not user.cgpa:
        flash('You have not completed any courses')
        return redirect(url_for('courses_get'))
    cgpa = f"{user.cgpa:.2f}"
    project_cgpa = f"{user.project_cgpa:.2f}" if user.project_cgpa else 'N/A'
    user_courses = user.user_courses
    courses = Course.query.all()
    courses = [ c for c in courses if c.course_code in [uc.course_code for uc in user_courses] ]
    user_courses = {user_course.course_code: user_course.grade for user_course in user_courses}
    calculation_string = "CGPA = (\n"
    for course in courses:
        calculation_string += str(course.course_code) + " (" + str(course.course_credits) + " credits) * " + str(user_courses[course.course_code].value) + " grade points + "
        calculation_string += "\n"
    calculation_string = calculation_string[:-3]
    calculation_string += ")\n÷\n("
    for course in courses:
        calculation_string += str(course.course_credits) + " + "
    calculation_string = calculation_string[:-3]
    calculation_string += ") credits"
    return render_template('cgpa.html',
                           cgpa=cgpa,
                           project_cgpa=project_cgpa,
                           project_cgpa_color = ('black' if project_cgpa == 'N/A' else 'red' if float(project_cgpa) < 7 else 'green'),
                           courses=courses,
                           user_courses=user_courses,
                           level=user.level,
                           calculation_string=calculation_string
                        )

@app.route('/forgetme', methods=['GET'])
def forgetme():
    """
    Route for clearing user data and starting over.
    """
    if 'session_id' in session:
        session.pop('session_id', None)
    return redirect(url_for('index'))
