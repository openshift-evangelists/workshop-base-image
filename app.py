import os
import json

from flask import (Flask, redirect, url_for, render_template,
        request, abort, send_from_directory)

from werkzeug.contrib.fixers import ProxyFix

from jinja2 import FileSystemLoader

from flask_misaka import Misaka

from courses import load_workshop, COURSES_DIRECTORY

# Create Flask application.

uri_root_path = os.environ.get('URI_ROOT_PATH', '')
static_url_path = uri_root_path + '/static'

app = Flask(__name__, static_url_path=static_url_path)

template_loader = FileSystemLoader([
        os.path.join(os.path.dirname(__file__), 'templates'),
        COURSES_DIRECTORY])

app.jinja_loader = template_loader

app.wsgi_app = ProxyFix(app.wsgi_app)

# Use Misaka for markdown rendering.

mikasa = Misaka(app, fenced_code=True)

# Load the details of the workshop.

workshop_details = load_workshop()

print(workshop_details)

# Set up request handlers.

default_page = os.environ.get('DEFAULT_PAGE', 'dashboard')

if uri_root_path:
    @app.route('/')
    def root():
        return redirect(url_for('home'))

@app.route(uri_root_path + '/')
def home():
    # Even if default page is the dashboard, redirect to the
    # terminal if there are no courses.

    if default_page == 'dashboard' and not workshop_details:
        return redirect(url_for('terminal'))

    return redirect(url_for(default_page))

@app.route(uri_root_path + '/terminal/')
def terminal():
    # Should never get here as the proxy should forward any
    # requests for here through to the terminal process.

    return 'whoops, how did I get here'

@app.route(uri_root_path + '/dashboard/')
def dashboard():
    return render_template("home.html", workshop=workshop_details)

@app.route(uri_root_path + '/workshop/')
def workshop():
    embedded = request.args.get('embedded')

    # If there is only one course, redirect to that course.

    if workshop_details and len(workshop_details['courses']) == 1:
        name = workshop_details['courses'][0]
        return redirect(url_for('course', name=name, embedded=embedded))

    return render_template("catalog.html", workshop=workshop_details,
            embedded=embedded)

@app.route(uri_root_path + '/course/<name>/')
def course(name):
    if not workshop_details:
        abort(404)

    if name not in workshop_details['index']:
        abort(404)

    course = workshop_details['index'][name]

    embedded = request.args.get('embedded')

    return render_template("course.html", workshop=workshop_details,
            course=course, embedded=embedded)

global_context = {
    'execute': '<button onclick="handle_execute(this)">Execute</button>',
    'copy': '<button onclick="handle_copy(this)">Copy</button>',
}

@app.route(uri_root_path + '/course/<name>/<path>')
def module(name, path):
    if not workshop_details:
        abort(404)

    if name not in workshop_details['index']:
        abort(404)

    course = workshop_details['index'][name]

    if path not in course['index']:
        abort(404)

    module = course['index'][path]

    filename = '%s/%s' % (name, module['file'])

    embedded = request.args.get('embedded')

    return render_template("module.html", workshop=workshop_details,
            course=course, module=module, filename=filename,
            embedded=embedded, **global_context)

@app.route(uri_root_path + '/course/<name>/images/<filename>')
def image(name, filename):
    return send_from_directory(COURSES_DIRECTORY, name+'/images/'+filename)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8081)
