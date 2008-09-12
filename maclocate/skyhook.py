import sys
import simplexmlapi
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientFactory
from twisted.web.client import getPage

class SkyhookProtocol(object):
    def __init__(self):
        self.parsed = 0
        self.with_errors = 0
        self.error_list = []
        self.results = []

    def error_handler(self, traceback, extra_args):
        print traceback, extra_args
        self.with_errors += 1
        self.error_list.append(extra_args)

    def xmlreq(self, macaddress, username="beta", realm="js.loki.com", 
                signalstrength="-50"):
        """
        Create the XML document to be posted to Skyhook.
        """
        macaddress = macaddress.replace(':','')
        return ("""<?xml version='1.0'?>
            <LocationRQ xmlns='http://skyhookwireless.com/wps/2005' 
                version='2.6' street-address-lookup='full'>
                <authentication version='2.0'>
                    <simple>
                        <username>%(username)s</username>
                        <realm>%(realm)s</realm>
                    </simple>
                </authentication>
                <access-point>
                    <mac>%(macaddress)s</mac>
                    <signal-strength>%(signalstrength)s</signal-strength>
                </access-point>
            </LocationRQ>
        """ % locals()).strip()

    def get(self, r, macaddress):
        postdata = self.xmlreq(macaddress)
        d = getPage('https://api.skyhookwireless.com/wps2/location',
                    method='POST', 
                    headers={'Content-Type':'text/xml'},
                    postdata=postdata)
        return d

    def parse(self, data, macaddress):
        doc = simplexmlapi.loads(data)
        try:
            result = doc.latitude._, doc.longitude._
        except:
            result = doc.error._
        return macaddress, result

    def store(self, result):
        self.results.append(result)

    def done(self, data=None):
        self.parsed += 1
        if self.parsed >= self.FINISHEDNUM:
            for mac, loc in self.results:
                print "%s\t%s" % (mac, loc)
            reactor.stop()

    def start(self, macaddresses, standalone=True):
        d = defer.succeed("Starting...")
        if standalone: self.FINISHEDNUM = len(macaddresses)
        for macaddress in macaddresses:
            d.addCallback(self.get, macaddress)
            d.addErrback(self.error_handler, (macaddress, 'getting'))

            d.addCallback(self.parse, macaddress)
            d.addErrback(self.error_handler, (macaddress, 'parsing'))

            d.addCallback(self.store)
            d.addErrback(self.error_handler, (macaddress, 'storing'))

            if standalone:
                d.addCallback(self.done)

        if not standalone:
            return d

class SkyhookFactory(ClientFactory):
    def __init__(self, macs, standalone=False):
        self.protocol = SkyhookProtocol()
        self.standalone = standalone
        if standalone:
            self.start(macs)

    def start(self, macs):
        """
        Might split into groups here so as not to flood server.
        """
        if not self.standalone:
            return self.protocol.start(macs, self.standalone)
        else:
            self.protocol.start(macs, self.standalone)

def locate(*macs):
    """
    Attempt to locate interfaces.
    """
    f = SkyhookFactory(macs, standalone=True)
    reactor.run()

def cli():
    macs = sys.argv[1:]
    locate(*macs)

