from urllib2 import Request, urlopen, URLError, HTTPError

class NetSpyPy:

    def scrape(self, url, user_agent):
        result = None
        headers = {'User-Agent': user_agent}
        request = Request(url, None, headers)

        try:
            urlfile = urlopen(request)
        except HTTPError, e:
            print e.code
        except URLError, e:
            print e.reason
        else:
            result = urlfile.read()
            urlfile.close()

        return result
