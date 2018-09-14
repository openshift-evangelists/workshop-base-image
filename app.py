import os
import json
import StringIO

from flask import (Flask, redirect, url_for, render_template,
        request, abort, send_from_directory)

from werkzeug.contrib.fixers import ProxyFix

from jinja2 import FileSystemLoader

from flask_misaka import Misaka
from asciidocapi import AsciiDocAPI

from workshop import load_workshop

# Create Flask application.

uri_root_path = os.environ.get('URI_ROOT_PATH', '')
static_url_path = uri_root_path + '/static'

app = Flask(__name__, static_url_path=static_url_path)

# Need to fix up host details when accessed via proxies. When we know we
# are running through JupyterHub, there will be two proxy values. We
# can't currently use Werkzeug ProxyFix class as version which supports
# multiple proxies not released yet.

#if os.environ.get('JUPYTERHUB_USER'):
#    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=2, x_port=2)
#else:
#    app.wsgi_app = ProxyFix(app.wsgi_app)

def proxy_fix(app):
    def _app(environ, start_response):
        proto = environ.get('HTTP_X_FORWARDED_PROTO')

        if proto:
            hops = proto.split(',')
            if os.environ.get('JUPYTERHUB_USER') and len(hops) > 1:
                environ['wsgi.url_scheme'] = hops[-2]
            else:
                environ['wsgi.url_scheme'] = hops[-1]

        port = environ.get('HTTP_X_FORWARDED_PORT')

        if port:
            hops = port.split(',')
            if os.environ.get('JUPYTERHUB_USER') and len(hops) > 1:
                environ['SERVER_PORT'] = hops[-2]
            else:
                environ['SERVER_PORT'] = hops[-1]

        return app(environ, start_response)

    return _app

app.wsgi_app = proxy_fix(app.wsgi_app)

# Setup markdown filter for formatting.

mikasa = Misaka(app, fenced_code=True)

# Setup asciidoc filter for formatting.

def asciidoc(value):
    output = value

    asciidoc = AsciiDocAPI()
    asciidoc.options('--no-header-footer')
    result = StringIO.StringIO()
    asciidoc.execute(StringIO.StringIO(output.encode('utf-8')),
        result, backend='html5')

    return unicode(result.getvalue(), "utf-8")

app.jinja_env.filters.setdefault('asciidoc', asciidoc)

# Load the details of the workshop.

workshop_info = load_workshop()

print(workshop_info)

# Setup search path for templates.

template_loader = FileSystemLoader([
        os.path.join(os.path.dirname(__file__), 'templates'),
        workshop_info.root])

app.jinja_loader = template_loader

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

    if default_page == 'dashboard' and not workshop_info:
        return redirect(url_for('terminal'))

    return redirect(url_for(default_page))

@app.route(uri_root_path + '/terminal/')
def terminal():
    # Should never get here as the proxy should forward any
    # requests for here through to the terminal process.

    return 'whoops, how did I get here'

@app.route(uri_root_path + '/dashboard/')
def dashboard():
    return render_template("dashboard.html", workshop=workshop_info)

@app.route(uri_root_path + '/workshop/')
def workshop():
    embedded = request.args.get('embedded')

    # If there is only one course, redirect to that course.

    if workshop_info and len(workshop_info.courses) == 1:
        name = workshop_info.courses[0]
        return redirect(url_for('course', name=name, embedded=embedded))

    return render_template("catalog.html", workshop=workshop_info,
            embedded=embedded)

@app.route(uri_root_path + '/course/<name>/')
def course(name):
    if not workshop_info:
        abort(404)

    if name not in workshop_info.details:
        abort(404)

    course_info = workshop_info.details[name]

    embedded = request.args.get('embedded')

    return render_template("course.html", workshop=workshop_info,
            course=course_info, embedded=embedded)

command_context = {
    'execute': '<button onclick="handle_execute(this)">Execute</button>',
    'copy': '<button onclick="handle_copy(this)">Copy</button>',
}

@app.route(uri_root_path + '/course/<name>/<path>')
def module(name, path):
    if not workshop_info:
        abort(404)

    if name not in workshop_info.details:
        abort(404)

    course_info = workshop_info.details[name]

    if path not in course_info.index:
        abort(404)

    module = course_info.index[path]

    filename = '%s/%s' % (name, module['file'])
    filetype = os.path.splitext(filename)[1]

    embedded = request.args.get('embedded')

    context = {}

    context.update(course_info.context)
    context.update(workshop_info.context)
    context.update(command_context)

    return render_template("module.html", workshop=workshop_info,
            course=course_info, module=module, filename=filename,
            filetype=filetype, embedded=embedded, **context)

@app.route(uri_root_path + '/course/<name>/images/<filename>')
def image(name, filename):
    return send_from_directory(workshop_info.root, name+'/images/'+filename)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8081)
