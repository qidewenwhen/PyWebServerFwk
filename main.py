from PyFwk import PyFwk
from PyFwk.view import Controller
from core.base_view import BaseView

class Index(BaseView):
	def get(self, request):
		return 'Hello this is a get'

class Test(Index):
	def post(self, request):
		return 'Hello this is a post'

app = PyFwk()

syl_url_map = [
	{
		'url': '/pyfwk',
		'view': Index,
		'endpoint': 'index'
	},
	{
		'url': '/test',
		'view': Test,
		'endpoint': 'test'
	}
]

index_controller = Controller('index', syl_url_map)
app.load_controller(index_controller)

app.run()

