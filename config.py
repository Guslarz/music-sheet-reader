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
LABEL_BG_COLOR = 'white'
LABEL_BBOX = dict(alpha=.5, color="white",
                  boxstyle="square,pad=0")


# CONFIG VARS
GLOBAL_DEBUG_LEVEL = DebugLevel.OFF
SAVE = True
