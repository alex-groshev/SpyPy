import sys

class SpyPyIo:

    def get_file_contents(self, file):
        try:
            with open(file) as f:
                return [line.strip() for line in f]
        except EnvironmentError as err:
            print "Unable to open file: {}".format(err)
            sys.exit(1)