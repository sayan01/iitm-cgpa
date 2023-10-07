#!/bin/env python3

from bs4 import BeautifulSoup as bs
import requests
import re
import json
def clean(s):
    s = re.sub("\n", "", s)
    s = re.sub("PROJECT ","", s)
    s = s.strip()
    s = " ".join(s.split())
    return s

URL="https://study.iitm.ac.in/ds/academics.html"
DEGREECOURSES="degree.csv"
OUTPUTFILE="iitm-courses.json"
page = requests.get(URL)
soup = bs(page.content, 'lxml')

# find all the tables
tables = soup.find_all('table')

courses = []

level = 1
foundational = []
diploma = []
for table in tables:
    ths = table.find_all('th')
    if len(ths) == 0:
        continue
    if "Course Name" in "".join([th.text for th in ths]):
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) == 0: continue
            prereq = tds[3].text.replace('None', '').replace(' ', '').replace(',', ' ').split()
            coreq = tds[4].text.replace('None', '').replace(' ', '').replace(',', ' ').split()
            if level == 1:
                foundational.append(tds[2].text)
            else:
                prereq.extend(foundational)
                diploma.append(tds[2].text)

            course = {
                'course_code': tds[2].text,
                'course_name': clean(tds[0].text),
                'course_credits': int(tds[1].text),
                'course_type': 'Theory' if len(tds[2].text.strip())==8 else 'Project',
                'course_level': level,
                'course_prereq': prereq,
                'course_coreq': coreq
            }
            courses.append(course)
        if level == 1: level += 1

level += 1

import csv
# read the degree level courses from the prescraped tsv file
with open(DEGREECOURSES, 'r') as ip:
    data = csv.DictReader(ip)
    for line in data:
        prereq = line['course_prereq'].replace(',',' ').split()
        prereq.extend(diploma)
        coreq = line['course_coreq'].replace(',',' ').split()
        course = {
            'course_code': line['course_code'],
            'course_name': line['course_name'],
            'course_credits': int(line['course_credits']),
            'course_type': line['course_type'],
            'course_level': level,
            'course_prereq': prereq,
            'course_coreq': coreq
        }
        courses.append(course)

with open(OUTPUTFILE, 'w') as op:
    json.dump(courses,op)
