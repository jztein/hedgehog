import webapp2
from jinja2 import Environment, PackageLoader
from cgi import escape

from google.appengine.ext import db

# TODO: what to do when there are no more promo-codes

TEST_PROMO_CODE = "happyhog-6a2b446t"

# jinja2 template classes
class Button:
    def __init__(self, string):
        self.answer = string

# datastore classes
class Promocode(db.Model):
    code = db.StringProperty(required=True)

    # NOTE: no expiry support for now (no info in exported document).
    # can do manual hacks of course
    #expiry = db.StringProperty(required=True) # or DateProperty?


def populateDB(exportedPCodes):
    print "populating db with new promocodes...."
    promocodes = [Promocode(code=epc[:-1]) for epc in exportedPCodes]
    db.put(promocodes)

    print "successfully put new promocodes to db!"


# TODO: Admin page requires login
class AdminPage(webapp2.RequestHandler):
    def get(self, uploadedPcodes=[], numPCs=0):
        env = Environment(loader=PackageLoader('pocketgame', 'templates'))
        template = env.get_template('president.html')
        self.response.write(template.render(pcodes=uploadedPcodes, num=numPCs))

    def post(self):
        text = self.request.get('promocodes')
        newPromocodes = text.split('\n')
        populateDB(newPromocodes)
        self.get(newPromocodes, len(newPromocodes))


class MainPage(webapp2.RequestHandler):
    def get(self, clearDB=False):
        self.response.headers['Content-Type'] = 'text/html'
        env = Environment(loader=PackageLoader('pocketgame', 'templates'))
        template = env.get_template('game.html')

        if clearDB:
            try:
                query = Promocode.all(keys_only=True)
                entries = query.run(batch_size=1000)
                db.delete(entries)
            except:
                print "couldn't delete"

        q = db.GqlQuery("SELECT * FROM Promocode")# WHERE code=:c", c=TEST_PROMO_CODE)
        discountCodeFailure = False

        try:
            pcObj = q.get()
        except:
            discountCodeFailure = True

        if pcObj == None:
            discountCodeFailure = True

        bs = []
        for i in xrange(12):
            if i != 2:
                bs.append(Button('emptyIm.src'))
            else:
                if discountCodeFailure:
                    bs.append(Button('emptyIm.src'))
                else:
                    bs.append(Button("hogIm.src; document.getElementById('info').innerHTML='%s'" % pcObj.code[:-1]))

        if discountCodeFailure:
            self.response.write(template.render(buttons=bs, promo="Discount codes unavailable"))
        else:
            self.response.write(template.render(buttons=bs, promo=""))


application = webapp2.WSGIApplication([
        ('/',MainPage),
        ('/president', AdminPage),
], debug=True)
