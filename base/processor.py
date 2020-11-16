from config import GLOBAL_DEBUG_LEVEL, DebugLevel


class Processor(object):
    def __init__(self, debug_level: DebugLevel=DebugLevel.OFF):
        self.debug_level_ = max(debug_level, GLOBAL_DEBUG_LEVEL)

    @property
    def debug_level(self):
        return self.debug_level_
