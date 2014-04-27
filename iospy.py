import sys

class IoSpyPy:

    @staticmethod
    def file_get_contents(file):
        try:
            with open(file) as f:
                return [line.strip() for line in f]
        except EnvironmentError as err:
            print "Unable to open file: {}".format(err)
            sys.exit(1)
