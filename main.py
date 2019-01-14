from PyFwk import PyFwk, simple_template, redirect
from PyFwk.view import Controller
from core.base_view import BaseView, SessionView
from PyFwk.session import session

class Index(SessionView):
	def get(self, request):
		user = session.get(request, 'user')
		return simple_template("index.html", user = user, message = "Hello World")

class Login(BaseView):
	def get(self, request):
		return simple_template("login.html")
	def post(self, request):
		user = request.form['user']
		session.push(request, 'user', user)
		return redirect('/')

class Logout(BaseView):
	def get(self, request):
		session.pop(request, 'user')
		return redirect('/')

syl_url_map = [
	{
		'url': '/',
		'view': Index,
		'endpoint': 'index'
	},
	{
		'url': '/login',
		'view': Login,
		'endpoint': 'login'
	},
	{
		'url': '/logout',
		'view': Logout,
		'endpoint': 'logout'
	}
]

app = PyFwk()

index_controller = Controller('index', syl_url_map)
app.load_controller(index_controller)

app.run()

