import sys
from ConfigParser import ConfigParser

class ConfSpyPy:

    @staticmethod
    def load(file):
        config = ConfigParser()
        config.read(file)

        # MongoDB settings
        host = config.get('MongoDB', 'host')
        port = config.getint('MongoDB', 'port')

        # Regex settings
        google_analytics = config.get('Regex', 'google_analytics')
        google_adsense = config.get('Regex', 'google_adsense')

        # Procspy
        threads = config.getint('Procspy', 'threads')

        if not host or not port or not google_analytics or not google_adsense or not threads:
            print 'Please, specify all required parameters in %s!' % file
            sys.exit(1)

        return {
            'host': host,
            'port': port,
            'google_analytics': google_analytics,
            'google_adsense': google_adsense,
            'threads': threads
        }
