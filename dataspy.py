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
