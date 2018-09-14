import os
import json

# The courses need to be placed under '/opt/app-root/workshop' directory.
# Two different ways of defining the course structure are currently
# supported. The first is to provide a 'workshop_config.py' in the top
# level directory, with a 'course_config.py' in the course directories.
# The second is to provide Katacoda style 'pathway.json' and 'index.json'
# files in the respective directories.

def load_workshop(root='/opt/app-root/workshop'):
    if os.path.exists(os.path.join(root, 'pathway.json')):
        return load_katacoda_workshop(root)

    if os.path.exists(os.path.join(root, 'workshop_config.py')):
        return load_workshop_config(root)

    return Workshop(root)

# Define classes to hold details for workshop and course. These are mainly
# to simplify access from configuration files.

class Workshop(object):

    def __init__(self, root):
        self.root = root
        self.title = 'Workshop'
        self.courses = []
        self.context = {}
        self.details = {}

class Course(object):

    def __init__(self, root, name):
        self.root = root
        self.name = name
        self.title = 'Course'
        self.modules = []
        self.context = {}
        self.details = {}

# Read and process the 'workshop_config.py' configuation file.

def load_workshop_config(root):
    return Workshop(root)

# Read and process Katacoda style 'pathway.json' file.

def load_katacoda_course(root, name):
    directory = os.path.join(root, name)
    course_file = os.path.join(root, name, 'index.json')

    if not os.path.exists(course_file):
        return

    with open(course_file) as fp:
        data = json.load(fp)

    if not 'details' in data:
        return

    if not 'steps' in data['details']:
        return

    course = Course(root, name)

    course.title = data.get('title')

    def create_module(entry, title=None):
        current = {}

        current['title'] = title or entry['title'] 
        current['file'] = entry['text']
        current['path'] = os.path.splitext(current['file'])[0] + '.html'

        current['previous'] = None
        current['next'] = None

        if course.modules:
            path = course.modules[-1]
            previous = course.details[path]
            previous['next'] = current['path']

        course.modules.append(current['path'])
        course.details[current['path']] = current

        return current

    if 'intro' in data['details']:
        if 'text' in data['details']['intro']:
            create_module(data['details']['intro'], 'Introduction')

    for entry in data['details']['steps']:
        create_module(entry)

    if 'finish' in data['details']:
        if 'text' in data['details']['finish']:
            create_module(data['details']['finish'], 'Summary')

    return course

def load_katacoda_workshop(root):
    pathway_file = os.path.join(root, 'pathway.json')

    if not os.path.exists(pathway_file):
        return

    with open(pathway_file) as fp:
        data = json.load(fp)

    workshop = Workshop(root)

    workshop.title = data.get('title')

    for course in data.get('courses', []):
        name = course.get('course_id')

        if name:
            course = load_katacoda_course(root, name)
            if course:
                workshop.courses.append(name)
                workshop.details[name] = course

    return workshop
