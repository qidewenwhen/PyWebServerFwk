class PyFwkException(Exception):
    def __init__(self, code = '', message = 'Error'):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message

class EndpointExistsError(PyFwkException):
    def __init__(self, message = 'Endpoint exists'):
        super(EndpointExistsError, self).__init__(message)

class URLExistsError(PyFwkException):
    def __init__(self, message = 'URL exists'):
        super(URLExistsError, self).__init__(message)
