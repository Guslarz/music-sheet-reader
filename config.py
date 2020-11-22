from enum import IntEnum


# ENUMS
class DebugLevel(IntEnum):
    OFF = 0
    REPORT = 1
    MAIN = 2
    ALL = 3


# CONSTANTS
OUT_DIR = 'resources/output'
OUT_EXT = 'jpg'


# CONFIG VARS
GLOBAL_DEBUG_LEVEL = DebugLevel.OFF
SAVE = False


