from PyFwk.view import View

class BaseView(View):
    methods = ['GET', 'POST']

    def post(self, request, *args, **options):
        pass

    def get(self, request, *args, **options):
        pass

    def router(self, request, *args, **options):
        methods_meta = {
                'GET': self.get,
                'POST': self.post
                }
        if request.method in methods_meta:
            return methods_meta[request.method](request, *args, **options)
        else:
            return '<h1>Unknown or unsupported require method</h1>'


