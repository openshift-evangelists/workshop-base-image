import os
import json

# The courses need to be placed under /opt/app-root/workshop directory.
# Expect to find a pathway.json file which lists the courses which are
# available. Each course needs to have a matching directory, and in that
# there needs to be an index.json file which describes the steps which
# make up the course. The format of these files is the same as is used
# in Katacoda to make porting easier.

COURSES_DIRECTORY = '/opt/app-root/workshop'

def load_course(name):
    course_file = os.path.join(COURSES_DIRECTORY, name, 'index.json')

    if not os.path.exists(course_file):
        return

    with open(course_file) as fp:
        data = json.load(fp)

    if not 'details' in data:
        return

    if not 'steps' in data['details']:
        return

    course_details = {}

    course_details['name'] = name

    course_details['title'] = data.get('title')

    course_details['modules'] = []
    course_details['index'] = {}

    def create_module(entry, title=None):
        current = {}

        current['title'] = title or entry['title'] 
        current['file'] = entry['text']
        current['path'] = os.path.splitext(current['file'])[0] + '.html'

        current['previous'] = None
        current['next'] = None

        if course_details['modules']:
            path = course_details['modules'][-1]
            previous = course_details['index'][path]
            previous['next'] = current['path']

        course_details['modules'].append(current['path'])
        course_details['index'][current['path']] = current

        return current

    if 'intro' in data['details']:
        if 'text' in data['details']['intro']:
            create_module(data['details']['intro'], 'Introduction')

    for entry in data['details']['steps']:
        create_module(entry)

    if 'finish' in data['details']:
        if 'text' in data['details']['finish']:
            create_module(data['details']['finish'], 'Summary')

    return course_details

def load_workshop():
    pathway_file = os.path.join(COURSES_DIRECTORY, 'pathway.json')

    if not os.path.exists(pathway_file):
        return

    with open(pathway_file) as fp:
        data = json.load(fp)

    workshop_details = {}

    workshop_details['title'] = data.get('title')

    print('workshop title:', workshop_details['title'])

    workshop_details['courses'] = []
    workshop_details['index'] = {}

    for course in data.get('courses', []):
        name = course.get('course_id')

        print('loading course:', name)

        if name:
            course_details = load_course(name)
            if course_details:
                workshop_details['courses'].append(name)
                workshop_details['index'][name] = course_details

    return workshop_details
