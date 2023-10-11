from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import enum
import json

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Level(enum.Enum):
    FOUNDATION = 1
    DIPLOMA = 2
    DEGREE = 3

class Grade(enum.Enum):
    S = 10
    A = 9
    B = 8
    C = 7
    D = 6
    E = 4

class User(db.Model):
    session_id = db.Column(db.String(36), primary_key=True)
    creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    level = db.Column(db.Enum(Level), nullable=False)
    cgpa = db.Column(db.Float, nullable=True, default=None)

    user_courses = db.relationship('UserCourse', backref='user', lazy=True)

    def calculate_cgpa(self):
        if len(self.user_courses) == 0:
            self.cgpa = None
            db.session.commit()
            return
        total_credits = 0
        total_grade_points = 0
        for user_course in self.user_courses:
            if user_course.grade.value < 1:
                continue
            total_credits += user_course.course.course_credits
            total_grade_points += user_course.course.course_credits * user_course.grade.value
        self.cgpa = total_grade_points / total_credits
        db.session.commit()

class UserCourse(db.Model):
    session_id = db.Column(db.String(36), db.ForeignKey('user.session_id'), primary_key=True)
    course_code = db.Column(db.String(10), db.ForeignKey('course.course_code'), primary_key=True)
    grade = db.Column(db.Enum(Grade), nullable=False)

class Course(db.Model):
    course_code = db.Column(db.String(10), primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_credits = db.Column(db.Integer, nullable=False)
    course_type = db.Column(db.String(20), nullable=False)
    course_level = db.Column(db.Enum(Level), nullable=False)

    course_prereq = db.relationship('Prerequisite', backref='course', lazy=True, foreign_keys='Prerequisite.course_code')
    course_coreq = db.relationship('Corequisite', backref='course', lazy=True, foreign_keys='Corequisite.course_code')
    user_courses = db.relationship('UserCourse', backref='course', lazy=True)

class Prerequisite(db.Model):
    course_code = db.Column(db.String(10), db.ForeignKey('course.course_code'), primary_key=True)
    prereq_code = db.Column(db.String(10), db.ForeignKey('course.course_code'), primary_key=True)

class Corequisite(db.Model):
    course_code = db.Column(db.String(10), db.ForeignKey('course.course_code'), primary_key=True)
    coreq_code = db.Column(db.String(10), db.ForeignKey('course.course_code'), primary_key=True)

with app.app_context():
    db.create_all()
    # add all the courses into the database
    with open('iitm-courses.json') as f:
        courses = json.load(f)
    for course in courses:
        course_code = course['course_code']
        course_name = course['course_name']
        course_credits = int(course['course_credits'])
        course_type = course['course_type']
        course_level = Level(int(course['course_level']))
        c = Course.query.get(course_code)
        if c:
            c.course_name = course_name
            c.course_credits = course_credits
            c.course_type = course_type
            c.course_level = course_level
        else:
            db.session.add(Course(course_code=course_code, course_name=course_name, course_credits=course_credits, course_type=course_type, course_level=course_level))
        prereq = course['course_prereq']
        for p in prereq:
            if Prerequisite.query.filter_by(course_code=course_code, prereq_code=p).first():
                continue
            db.session.add(Prerequisite(course_code=course_code, prereq_code=p))
        for p in Prerequisite.query.filter_by(course_code=course_code).all():
            if p.prereq_code not in prereq:
                db.session.delete(p)
        coreq = course['course_coreq']
        for c in coreq:
            if Corequisite.query.filter_by(course_code=course_code, coreq_code=c).first():
                continue
            db.session.add(Corequisite(course_code=course_code, coreq_code=c))
        for c in Corequisite.query.filter_by(course_code=course_code).all():
            if c.coreq_code not in coreq:
                db.session.delete(c)
        db.session.commit()