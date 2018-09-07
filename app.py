import os
import json

from flask import (Flask, redirect, url_for, render_template,
        request, abort, send_from_directory)

from flask_misaka import Misaka

app = Flask(__name__)
mikasa = Misaka(app, fenced_code=True)

course_directory = '/opt/app-root/workshop'
course_index_file = os.path.join(course_directory, 'index.json')

course = {}

if os.path.exists(course_index_file):
    with open(course_index_file) as fp:
        course = json.load(fp)

course_modules = {}

previous = None
current = None

if course:
    for current in course['details']['steps']:
        current['path'] = os.path.splitext(current['text'])[0] + '.html'
        course_modules[current['path']] = current

        current['previous'] = previous and previous['path']

        if previous:
            previous['next'] = current['path']

        previous = current

    if current:
        current['next'] = None

uri_root_path = os.environ.get('URI_ROOT_PATH', '')
default_page = os.environ.get('DEFAULT_PAGE', 'dashboard')

if uri_root_path:
    @app.route('/')
    def root():
        return redirect(url_for('home'))

@app.route(uri_root_path + '/')
def home():
    if default_page == 'dashboard' and not course:
        return redirect(url_for('terminal'))

    return redirect(url_for(default_page))

@app.route(uri_root_path + '/terminal/')
def terminal():
    return 'whoops, how did I get here'

@app.route(uri_root_path + '/dashboard/')
def dashboard():
    return render_template("home.html", course=course)

@app.route(uri_root_path + '/workshop/')
def workshop():
    embedded = request.args.get('embedded')

    return render_template("modules-list.html", course=course,
            embedded=embedded)

@app.route(uri_root_path + '/workshop/<module>')
def workshop_module(module):
    if not course:
        abort(404)

    if module not in course_modules:
        abort(404)

    filename = 'content/%s' % course_modules[module]['text']

    embedded = request.args.get('embedded')

    execute = '<button onclick="handle_command_execute(this)">Execute</button>'
    copy = '<button onclick="handle_text_copy(this)">Copy</button>'

    return render_template("module-file.html",
            module=course_modules[module], filename=filename,
            embedded=embedded, execute=execute, copy=copy)

@app.route(uri_root_path + '/workshop/images/<image>')
def image_file(image):
    return send_from_directory(course_directory+'/images', image)

@app.route(uri_root_path + '/static/<path:filename>')
def static_file(filename):
    return send_from_directory(os.path.dirname(__file__)+'/static', filename)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8081)
