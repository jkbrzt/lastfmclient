class Package(object):

    def __init__(self, client):
        self.client = client
        self.name = type(self).__name__.lower()

    def call(self, http_method, method, auth, **params):
        method = '%s.%s' % (self.name, method)
        return self.client.call(http_method, method, auth, params)
