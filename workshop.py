import os
import json
import imp

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
        self.index = {}

# The courses need to be placed under '/opt/app-root/workshop'
# directory. You need to provide a 'workshop_config.py' in the top level
# directory, with a 'course_config.py' in the course directories.

def update_navigation(course):
    previous = None

    for module in course.modules:
        module['path'] = os.path.splitext(module['file'])[0] + '.html'

        module['previous'] = previous
        module['next'] = None

        if previous:
            previous['next'] = module

        previous = module

        course.index[module['path']] = module

def load_workshop(root='/opt/app-root/workshop'):
    workshop_config = os.path.join(root, 'workshop_config.py')

    print('Loading workshop config %s.' % workshop_config)

    workshop = Workshop(root)

    if not os.path.exists(workshop_config):
        return workshop

    workshop_module = imp.new_module('__workshop__')
    workshop_module.__file__ = workshop_config
    workshop_module.workshop = workshop

    with open(workshop_config, 'r') as fp:
	code = compile(fp.read(), workshop_config, 'exec', dont_inherit=True)
	exec(code, workshop_module.__dict__, {})

    for name in workshop.courses:
        course_config = os.path.join(root, name, 'course_config.py')

        print('Loading course config %s.' % workshop_config)

	if not os.path.exists(course_config):
	    continue

        course = Course(root, name)

	course_module = imp.new_module('__course__')
	course_module.__file__ = course_config
	course_module.course = course

	with open(course_config, 'r') as fp:
	    code = compile(fp.read(), course_config, 'exec', dont_inherit=True)
	    exec(code, course_module.__dict__, {})

	if course.modules:
	    workshop.details[name] = course

    update_navigation(course)

    return workshop
