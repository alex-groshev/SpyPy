import sys
from pymongo import MongoClient

class DataSpyPy:
    
    def __init__(self, host, port):
        client = MongoClient(host, port)
        db = client.spypy
        self.collection = db.domains

    def insert_record(self, doc):
        try:
            self.collection.insert(doc)
        except:
            print 'Unexpected error:', sys.exc_info()[0], sys.exc_info()[1]

    def update_record(self, spec, doc):
        try:
            self.collection.update(spec, doc)
        except:
            print 'Unexpected error:', sys.exc_info()[0], sys.exc_info()[1]

    def get_unprocessed_records(self, limit):
        query = {'processed': 0}
        show = {'_id': 1, 'domain': 1}

        try:
            return list(self.collection.find(query, show).limit(limit))
        except:
            print 'Unexpected error:', sys.exc_info()[0], sys.exc_info()[1]        
