import sys
import re
import random
import socket
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
from iospy import IoSpyPy
from netspy import NetSpyPy


class ProcSpyPy:

    def __init__(self, dataspypy, google_analytics, google_adsense):
        self.dataspypy = dataspypy
        self.google_analytics = google_analytics
        self.google_adsense = google_adsense

        iospypy = IoSpyPy()
        self.user_agents = iospypy.file_get_contents('useragents.txt')

        self.netspypy = NetSpyPy()

    def get_random_item(self, list):
        return random.choice(list)

    def prepare_url(self, url):
        return 'http://' + url if not url.startswith('http://') else url

    def get_content(self, url):
        return self.netspypy.scrape(url, self.get_random_item(self.user_agents))

    def process(self, url):
        url = self.prepare_url(url)
        content = self.get_content(url)
        soup = BeautifulSoup(content)

        # Getting title
        title = soup.title.string
        title = title.encode('utf-8')

        # Getting description meta tag
        description = soup.find('meta', {"name": "description"})
        description = description['content'] if description != None else ''
        description = description.encode('utf-8')
        
        # Getting keywords meta tag
        keywords = soup.find('meta', {"name": "keywords"})
        if keywords != None:
            keywords = keywords['content'].split(',')
            keywords = [keyword.strip().encode('utf-8') for keyword in keywords]
        else:
            keywords = []

        # Getting Google Analytics code
        regex = re.compile(self.google_analytics, re.S+re.I)
        m = regex.search(content)
        google_analytics = m.group(1) if m else ''

        # Getting Google AdSense code
        regex = re.compile(self.google_adsense, re.S+re.I)
        m = regex.search(content)
        google_adsense = m.group(1) if m else ''

        # Getting domain name from URL
        u = urlparse(url)
        domain = u.netloc

        # Getting IP address
        ip = socket.gethostbyname(domain)

        doc = {
            'date': datetime.utcnow(),
            'domain': domain,
            'ip': ip,
            'url': url,
            'title': title,
            'description': description,
            'keywords': keywords,
            'analytics': google_analytics,
            'adsense': google_adsense,
            'processed': 1
        }

        return doc

    def process_urls(self, urls):
        if len(urls) < 1:
            print 'Please, specify URL(s)!'
            sys.exit(1)

        for url in urls:
            doc = self.process(url)

            print 'Inserting record: %s' % doc['domain']

            self.dataspypy.insert_record(doc)

        print 'Done'

    def process_records(self, records):
        if len(records) < 1:
            print 'Please, specify records to process!'
            sys.exit(1)

        for record in records:
            doc = self.process(record['domain'])

            rec = {
                '$set' : {
                    'date': datetime.utcnow(),
                    'ip': doc['ip'],
                    'url': doc['url'],
                    'title': doc['title'].encode('utf-8'),
                    'description': doc['description'].encode('utf-8'),
                    'keywords': doc['keywords'],
                    'analytics': doc['analytics'],
                    'adsense': doc['adsense'],
                    'processed': 1
                }
            }

            print 'Updating record: %s' % record['_id']

            self.dataspypy.update_record({'_id': record['_id']}, rec)

        print 'Done'

