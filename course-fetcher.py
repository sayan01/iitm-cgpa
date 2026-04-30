import csv
import json

FOUNDATION = "foundation.csv"
DIPLOMA = "diploma.csv"
DEGREE = "degree.csv"
OUTPUTFILE = "iitm-courses.json"


def parse_list(field):
    return [c.strip() for c in field.split(',') if c.strip()]


def read_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(filter(lambda row: row.strip(), f))
        return list(reader)


courses = []
foundational = []
diploma = []

for row in read_csv(FOUNDATION):
    foundational.append(row['course_code'])
    courses.append({
        'course_code': row['course_code'],
        'course_name': row['course_name'],
        'course_credits': int(row['course_credits']),
        'course_type': row['course_type'],
        'course_level': 1,
        'course_prereq': parse_list(row['course_prereq']),
        'course_coreq': parse_list(row['course_coreq']),
    })

for row in read_csv(DIPLOMA):
    prereq = parse_list(row['course_prereq'])
    prereq.extend(foundational)
    diploma.append(row['course_code'])
    courses.append({
        'course_code': row['course_code'],
        'course_name': row['course_name'],
        'course_credits': int(row['course_credits']),
        'course_type': row['course_type'],
        'course_level': 2,
        'course_prereq': prereq,
        'course_coreq': parse_list(row['course_coreq']),
    })

for row in read_csv(DEGREE):
    prereq = parse_list(row['course_prereq'])
    prereq.extend(diploma)
    courses.append({
        'course_code': row['course_code'],
        'course_name': row['course_name'],
        'course_credits': int(row['course_credits']),
        'course_type': row['course_type'],
        'course_level': 3,
        'course_prereq': prereq,
        'course_coreq': parse_list(row['course_coreq']),
    })

with open(OUTPUTFILE, 'w', encoding='utf-8') as op:
    json.dump(courses, op)
