import webapp2
from jinja2 import Environment, PackageLoader
from cgi import escape
import random
import datetime

from google.appengine.ext import db

# TODO: what to do when there are no more promo-codes

TEST_PROMO_CODE = "happyhog-6a2b446t"

random.seed()

class Button():
    def __init__(self, idx='1', string=''):
        self.idx = idx
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
        template_stop = env.get_template('killjoy.html')

        # if it's not one day yet, the user can't play yet
        cookie = self.request.cookies
        print "bottle o' rum Cookie:", cookie

        bs = []
        for i in xrange(12):
            bs.append(Button(str(i), 'moo'))


        if cookie.get('clock'):
            self.response.write(template_stop.render(buttons=bs))
            return
        else:
            # no cookie, so set a cookie
            # debug set low seconds
            expires_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
            expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
            expires_str = "Expires = %s" % expires_str
            self.response.headers.add_header('Set-Cookie', 'clock=1; %s' % expires_str)


        discountCodeFailure = False

        if clearDB:
            try:
                query = Promocode.all(keys_only=True)
                entries = query.run(batch_size=1000)
                db.delete(entries)
            except:
                print "couldn't delete"

        #for i in xrange(12):
        #    bs.append(Button('javascript:GetAnswer()'))
        '''
            if i != 2:
                bs.append(Button('emptyIm.src'))
            else:
                if discountCodeFailure:
                    bs.append(Button('emptyIm.src'))
                else:
                    bs.append(Button("hogIm.src; document.getElementById('info').innerHTML='%s'" % pcObj.code[:-1]))
            '''

        
        if discountCodeFailure:
            self.response.write(template.render(buttons=bs, promo="Discount codes unavailable"))
        else:
            self.response.write(template.render(buttons=bs, promo=""))


class GetCodeHandler(webapp2.RequestHandler):
    def get(self):
        button = """<img src='assets/dullhog.jpg' onclick='this.src="assets/emptyplate.jpg" ' />"""

        # only ask for promocode with low probability
        # CURRENTLY: 5% of players will get a pop
        if random.random() > 0.05:
            self.response.write(button)
            return

        q = db.GqlQuery("SELECT * FROM Promocode")

        discountCodeFailure = False
        try:
            pcObj = q.get()
        except:
            discountCodeFailure = True

        if pcObj == None:
            discountCodeFailure = True

        if discountCodeFailure:
            self.response.write(button)
            return
        
        button = """<img src='assets/dullhog.jpg' onclick='this.src="assets/hedgehog.jpg"; document.getElementById("info").innerHTML="%s" ' />""" % pcObj.code

        print "\n\n\n******* DELETED * ( %s ) *******\n\n\n" % pcObj.code

        # got code, delete it so that we don't repeat
        db.delete(pcObj)

        self.response.write(button)
        return


application = webapp2.WSGIApplication([
        ('/',MainPage),
        ('/president', AdminPage),
        ('/getanswer', GetCodeHandler),
], debug=True)
