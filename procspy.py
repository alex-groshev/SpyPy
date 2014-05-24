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
        self.user_agents = IoSpyPy.file_get_contents('useragents.txt')

    def get_random_item(self, list):
        return random.choice(list)

    def prepare_url(self, url):
        return 'http://' + url if not url.startswith('http://') else url

    def get_content(self, url):
        return NetSpyPy.scrape(url, self.get_random_item(self.user_agents))

    def process(self, url):
        url = self.prepare_url(url)
        content = self.get_content(url)

        if content is None:
            return None

        soup = BeautifulSoup(content.text)

        # Getting title
        title = ''
        if soup.title and soup.title.string:
            title = soup.title.string.encode('utf-8')

        # Getting description meta tag
        description = soup.find('meta', {"name": "description"})
        description = description['content'] if description is not None and description.has_key('content') else ''
        description = description.encode('utf-8')
        
        # Getting keywords meta tag
        keywords = soup.find('meta', {"name": "keywords"})
        if keywords is not None and keywords.has_key('content'):
            keywords = keywords['content'].split(',')
            keywords = [keyword.strip().encode('utf-8') for keyword in keywords]
        else:
            keywords = []

        # Getting Google Analytics code
        regex = re.compile(self.google_analytics, re.S+re.I)
        m = regex.search(content.text)
        google_analytics = m.group(1) if m else ''

        # Getting Google AdSense code
        regex = re.compile(self.google_adsense, re.S+re.I)
        m = regex.search(content.text)
        google_adsense = m.group(1) if m else ''

        # Getting domain name from URL
        u = urlparse(url)
        domain = u.netloc

        # Getting IP address
        ip = socket.gethostbyname(domain)

        # Getting data from headers
        server = content.headers['server'] if 'server' in content.headers else ''
        header_fields = {}
        header_fields_values = ['x-powered-by', 'x-aspnet-version', 'x-aspnetmvc-version', 'set-cookie']
        for field in header_fields_values:
            if field in content.headers:
                header_fields.update({field: content.headers[field]})

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
            'server': server,
            'hfields': header_fields,
            'processed': 1
        }

        return doc

    def process_urls(self, urls):
        if len(urls) < 1:
            print 'Please, specify URL(s)!'
            sys.exit(1)

        for url in urls:
            doc = self.process(url)

            if not doc:
                doc = {
                    'date': datetime.utcnow(),
                    'url': url,
                    'processed': 1,
                    'error': 1
                }

            print 'Inserting record: %s' % doc['url']

            self.dataspypy.insert_record(doc)

        print 'Done'

    def process_records(self, records):
        if len(records) < 1:
            print 'Please, specify records to process!'
            sys.exit(1)

        for record in records:
            if 'domain' not in record:
                continue

            doc = self.process(record['domain'])

            if not doc:
                rec = {
                    '$set': {
                        'date': datetime.utcnow(),
                        'domain': record['domain'],
                        'processed': 1,
                        'error': 1
                    }
                }
            else:
                rec = {
                    '$set': {
                        'date': datetime.utcnow(),
                        'ip': doc['ip'],
                        'url': doc['url'],
                        'title': doc['title'],
                        'description': doc['description'],
                        'keywords': doc['keywords'],
                        'analytics': doc['analytics'],
                        'adsense': doc['adsense'],
                        'server': doc['server'],
                        'hfields': doc['hfields'],
                        'processed': 1
                    }
                }

            print 'Updating record: %s - %s' % (record['_id'], record['domain'])

            self.dataspypy.update_record({'_id': record['_id']}, rec)

        print 'Done'
