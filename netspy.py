from urllib2 import Request, urlopen, URLError, HTTPError
from httplib import BadStatusLine, IncompleteRead

class NetSpyPy:

    def scrape(self, url, user_agent):
        result = None
        headers = {'User-Agent': user_agent}
        request = Request(url, None, headers)

        try:
            urlfile = urlopen(request)
            result = urlfile.read()
            urlfile.close()
        except HTTPError, e:
            print e.code
        except URLError, e:
            print e.reason
        except BadStatusLine, e:
            print e
        except IncompleteRead, e:
            print e

        return result
