import sys
import re
import random
import socket
import threading
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

    def prepare_document(self, url):
        url = ProcSpyPy.__prepare_url(url)
        content = self.__get_content(url)

        if content is None:
            return None

        try:
            soup = BeautifulSoup(content.text)
        except ValueError, e:
            print e
            return None

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
                if ProcSpyPy.__is_utf8(content.headers[field]):
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

    def process_url(self, url):
        if url is None:
            print 'Please, specify URL!'
            sys.exit(1)

        doc = self.prepare_document(url)
        if not doc:
            doc = {'date': datetime.utcnow(), 'url': url, 'processed': 1, 'error': 1}

        print 'Inserting record: %s' % doc['url']
        self.dataspypy.insert_record(doc)

    def process_urls(self, urls):
        for url in urls:
            self.process_url(url)

    def process_document(self, document):
        if document is None:
            print 'Please, specify record to process!'
            sys.exit(1)

        if 'domain' not in document:
            return None

        doc = self.prepare_document(document['domain'])

        if not doc:
            rec = {
                '$set': {
                    'date': datetime.utcnow(),
                    'domain': document['domain'],
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

        print 'Updating record: %s - %s' % (document['_id'], document['domain'])
        self.dataspypy.update_record({'_id': document['_id']}, rec)

    def process_documents(self, documents):
        for document in documents:
            self.process_document(document)

    @staticmethod
    def __get_random_item(list):
        return random.choice(list)

    @staticmethod
    def __prepare_url(url):
        return 'http://' + url if not url.startswith('http://') else url

    def __get_content(self, url):
        return NetSpyPy.scrape(url, ProcSpyPy.__get_random_item(self.user_agents))

    @staticmethod
    def __is_utf8(string):
        try:
            string.decode('utf8')
            return True
        except UnicodeDecodeError:
            return False


class DocumentProcessor(threading.Thread):
    def __init__(self, queue, procspypy):
        threading.Thread.__init__(self)
        self.queue = queue
        self.procspypy = procspypy

    def run(self):
        while True:
            record = self.queue.get()
            try:
                self.procspypy.process_document(record)
            except Exception, e:
                print e
            self.queue.task_done()
