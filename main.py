from PyFwk import PyFwk, simple_template, redirect, render_json, render_file
from PyFwk.view import Controller
from core.base_view import BaseView, SessionView
from PyFwk.session import session
from core.database import dbconn

class Index(SessionView):
	def get(self, request):
		user = session.get(request, 'user')
		return simple_template("index.html", user = user, message = "Hello World")

class Login(BaseView):
	def get(self, request):
		state = request.args.get('state', '1')
		return simple_template("layout.html", title = 'login', message = 'please input username' if state == "1" else "error for username, please input again")
	def post(self, request):
		ret = dbconn.execute('''SELECT * FROM user WHERE f_name = %(user)s''', request.form)
		if ret.rows == 1:
			user = ret.get_first()['f_name']
			session.push(request, 'user', user)
			return redirect("/")
		return redirect("/login?state=0")

class Logout(BaseView):
	def get(self, request):
		session.pop(request, 'user')
		return redirect('/')

class Register(BaseView):
	def  get(self, request):
		return simple_template("layout.html", title = "SignUp", message = "Please input username")

	def post(self, request):
		ret = dbconn.insert('INSERT INTO user(f_name) VALUES(%(user)s)', request.form)
		if ret.suc:
			return redirect("/login")
		else:
			return render_json(ret.to_dict())

class Download(BaseView):
	def get(self, request):
		return render_file('main.py')

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
	},
	{
		'url': '/register',
		'view': Register,
		'endpoint': 'register'
	}
]

app = PyFwk()

index_controller = Controller('index', syl_url_map)
app.load_controller(index_controller)

app.run()

