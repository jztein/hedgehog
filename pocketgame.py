import webapp2
from jinja2 import Environment, PackageLoader

class Button:
    def __init__(self, string):
        self.answer = string

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        env = Environment(loader=PackageLoader('pocketgame', 'templates'))
        template = env.get_template('game.html')
        bs = []
        for i in xrange(12):
            if i != 2:
                bs.append(Button('emptyIm.src'))
            else:
                bs.append(Button('hogIm.src; boris();'))
        self.response.write(template.render(buttons=bs, promo='fetch'))


application = webapp2.WSGIApplication([
        ('/',MainPage),
], debug=True)
