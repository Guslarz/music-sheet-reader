from enum import Enum
from numpy import array


class MusicalObject(object):
    def __init__(self, line_selection: array,
                 global_selection: array, order: int):
        self.line_selection_ = line_selection
        self.global_selection_ = global_selection
        self.order_ = order

    @property
    def order(self):
        return self.order_

    @property
    def line_selection(self):
        return self.line_selection_

    @property
    def global_selection(self):
        return self.global_selection_

    @property
    def type(self) -> Enum:
        pass


class Clef(MusicalObject):
    class Type(Enum):
        G_CLEF = 0,
        F_CLEF = 1

    def __init__(self, clef_type: Type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_ = clef_type

    @property
    def type(self):
        return self.type_

    def __str__(self):
        return f"Clef(type={self.type}, order={self.order})"


class Note(MusicalObject):
    class Type(Enum):
        WHOLE_NOTE = 0,
        HALF_NOTE = 1,
        QUARTER_NOTE = 2,
        EIGHTH_NOTE = 3

    def __init__(self, note_type: Type, tone: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_ = note_type
        self.tone_ = tone

    @property
    def type(self):
        return self.type_

    @property
    def tone(self):
        return self.tone_

    def __str__(self):
        return f"Note(type={self.type}, " \
            f"tone={self.tone}, order={self.order})"
