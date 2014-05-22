import requests


class NetSpyPy:

    @staticmethod
    def scrape(url, user_agent, timeout=10):
        result = None

        try:
            response = requests.get(url, headers={'User-Agent': user_agent}, timeout=timeout)
            if response.status_code == requests.codes.ok:
                result = response.text
        except Exception, e:
            print e

        return result
