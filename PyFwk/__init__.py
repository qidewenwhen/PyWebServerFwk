from werkzeug.serving import run_simple
from werkzeug.wrappers import Response
from PyFwk.wsgi_adapter import wsgi_app
import os
import json
import PyFwk.exceptions as exceptions
from PyFwk.helper import parse_static_key
from PyFwk.route import Route
from PyFwk.template_engine import replace_template
from PyFwk.session import create_session_id, session

ERROR_MAP = {
        '401': Response('<h1>401 Unknown or unsupported method</h1>', content_type = 'text/html; charset = UTF-8', status = 404),
        '404': Response('<h1>404 Source Not Found</h1>', content_type = 'text/html; charset = UTF-8', status = 404),
        '503': Response('<h1>503 Unknown function type</h1>', content_type = 'text/html; charset = UTF-8', status = 503)
        }

TYPE_MAP = {
        'css': 'text/css',
        'js': 'text/js',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg'
        }

def redirect(url, status_code = 302):
    response = Response(status = status_code)
    response.headers['Location'] = url
    return response

def simple_template(path, **options):
    return replace_template(PyFwk, path, **options)

def render_json(data):
    content_type = 'text/plain'
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
        content_type = 'application/json'
    return Response(data, content_type="%s; charset=UTF-8" % content_type, status = 200)

def render_file(file_path, file_name = None):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        if file_name is None:
            file_name = file_path.split("/")[-1]
        headers = {
            'Content-Disposition': 'attachment; file_name=%s' % file_name
        }
        return Response(content, headers = headers, status = 200)
    return ERROR_MAP['404']

class ExecFunc:
    def __init__(self, func, func_type, **options):
        self.func = func
        self.func_type = func_type
        self.options = options

class PyFwk:
    template_folder = None

    def __init__(self, static_folder = 'static', template_folder = 'template', session_path = '.session'):
        self.host = '127.0.0.1'
        self.port = 8086
        self.url_map = {}
        self.static_map = {}
        self.function_map = {}
        self.static_folder = static_folder
        self.template_folder = template_folder
        PyFwk.template_folder = self.template_folder
        self.route = Route(self)
        self.session_path = session_path

    def router(self, request):
        url = "/" + "/".join(request.url.split("/")[3:]).split("?")[0]
        if url.find(self.static_folder) == 1 and url.index(self.static_folder) == 1:
            endpoint = 'static'
            url = url[1:]
        else:
            endpoint = self.url_map.get(url, None)

        cookies = request.cookies
        if 'session_id' not in cookies:
            headers = {
                'Set-Cookie': 'session_id=%s' % create_session_id(),
                'Server': 'PyFwk'
            }
        else:
            headers = {'Server': 'PyFwk'}

        if endpoint is None:
            return ERROR_MAP['404']
        exec_function = self.function_map[endpoint]
        if exec_function.func_type == 'route':
            if request.method in exec_function.options.get('methods'):
                argcount = exec_function.func.__code__.co_argcount
                if argcount > 0:
                    rep = exec_function.func(request)
                else:
                    rep = exec_function.func()
            else:
                return ERROR_MAP['401']
        elif exec_function.func_type == 'view':
            rep = exec_function.func(request)
        elif exec_function.func_type == 'static':
            return exec_function.func(url)
        else:
            return ERROR_MAP['503']

        status = 200
        content_type = 'text/html'

        if isinstance(rep, Response):
            return rep
        return Response(rep, content_type = '%s; charset = UTF-8' % content_type, headers = headers, status = status)

    def router_static(self, static_path):
        if os.path.exists(static_path):
            key = parse_static_key(static_path)
            doc_type = TYPE_MAP.get(key, 'text/plain')
            with open(static_path, 'rb') as f:
                rep = f.read()
            return Response(rep, content_type = doc_type)
        else:
            return ERROR_MAP['404']

    def run(self, host = None, port = None, **options):
        for key, value in options.items():
            if value:
                self.__setattr__(key, value)

        if host:
            self.host = host

        if port:
            self.port = port

        self.function_map['static'] = ExecFunc(func = self.router_static, func_type = 'static')

        if not os.path.exists(self.session_path):
            os.mkdir(self.session_path)

        session.set_storage_path(self.session_path)

        session.load_local_session()

        run_simple(hostname = self.host, port = self.port, application = self, **options)

    def __call__(self, environ, start_response):
        return wsgi_app(self, environ, start_response)

    def add_url_rule(self, url, func, func_type, endpoint = None, **options):
        if endpoint is None:
            endpoint = func.__name__

        if url in self.url_map:
            raise exceptions.URLExistsError

        if endpoint in self.function_map and func_type != 'static':
            raise exceptions.EndpointExistsError

        self.url_map[url] = endpoint

        self.function_map[endpoint] = ExecFunc(func, func_type, **options)

    def bind_view(self, url, view_class, endpoint):
        self.add_url_rule(url, func = view_class.get_func(endpoint), func_type = 'view')

    def load_controller(self, controller):
        name = controller.__name__()
        for rule in controller.url_map:
            self.bind_view(rule['url'], rule['view'], name + '.' + rule['endpoint'])


