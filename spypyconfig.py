from ConfigParser import ConfigParser

class SpyPyConfig:

    def load(self, file):
        config = ConfigParser()
        config.read(file)

        # MongoDB settings
        host = config.get('MongoDB', 'host')
        port = config.getint('MongoDB', 'port')

        # Regex settings
        google_analytics = config.get('Regex', 'google_analytics')
        google_adsense = config.get('Regex', 'google_adsense')

        return {
            'host': host,
            'port': port,
            'google_analytics': google_analytics,
            'google_adsense': google_adsense
        }
