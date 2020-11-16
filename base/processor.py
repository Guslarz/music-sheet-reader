from config import DEBUG_ALL


class Processor(object):
    def __init__(self, debug=False):
        self.debug_ = debug or DEBUG_ALL
