import framework

class Tenant:

    @property
    def id(self):
        return framework.ctx['domain'].hostname.split('.')[0]

    @property
    def auth(self):
        return "OAUTH"