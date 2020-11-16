from enum import IntEnum


# ENUMS
class DebugLevel(IntEnum):
    OFF = 0
    MAIN = 1
    ALL = 2


# CONSTANTS
OUT_DIR = 'output'
OUT_EXT = 'jpg'


# CONFIG VARS
GLOBAL_DEBUG_LEVEL = DebugLevel.ALL
SAVE = False


