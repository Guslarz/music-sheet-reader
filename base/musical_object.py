from config import SAVE, OUT_DIR, OUT_EXT, \
    LABEL_BBOX

from enum import Enum
from numpy import array, mean
from matplotlib.pyplot import plot, text, \
    clf, savefig, show, figure


class MusicalObject(object):
    COLORS = {}

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

    def show(self):
        points = self.global_selection_
        plot(points[:, 1], points[:, 0],
             color=self.__class__.COLORS[self.type])

        order_pos = mean(points[:2, :], axis=0)
        text(order_pos[1], order_pos[0],
             f"{self.order_}",
             verticalalignment="bottom",
             horizontalalignment="center",
             bbox=LABEL_BBOX)

    @staticmethod
    def show_legend():
        classes = [Clef, Note]
        data = [(str(obj_type), cls.COLORS[obj_type])
                for cls in classes
                for obj_type in cls.Type]
        labels, colors = zip(*data)

        lines = [plot((0, 1), (0, 1), color=color)[0]
                 for color in colors]
        clf()

        fig_legend = figure(figsize=(2, 1.25))
        fig_legend.legend(lines, labels, loc='center', frameon=False)

        if SAVE:
            filename = f"{OUT_DIR}/legend.{OUT_EXT}"
            savefig(filename)
        else:
            show()
        clf()


class Clef(MusicalObject):
    class Type(Enum):
        G_CLEF = 0,
        F_CLEF = 1

        def __str__(self):
            return Clef.LABELS[self]

    COLORS = {
        Type.G_CLEF: 'black',
        Type.F_CLEF: 'pink'
    }

    LABELS = {
        Type.G_CLEF: 'klucz wiolinowy',
        Type.F_CLEF: 'klucz basowy'
    }

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

        def __str__(self):
            return Note.LABELS[self]

    COLORS = {
        Type.WHOLE_NOTE: 'blue',
        Type.HALF_NOTE: 'green',
        Type.QUARTER_NOTE: 'gold',
        Type.EIGHTH_NOTE: 'red'
    }

    LABELS = {
        Type.WHOLE_NOTE: 'cała nuta',
        Type.HALF_NOTE: 'półnuta',
        Type.QUARTER_NOTE: 'ćwierćnuta',
        Type.EIGHTH_NOTE: 'ósemka'
    }

    TONES = [
        'C', 'D', 'E', 'F',
        'G', 'A', 'H'
    ]

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

    def show(self):
        super().show()

        label_pos = mean(self.global_selection_[2:4, :],
                         axis=0)
        tone = self.tone_ % 7
        octave = self.tone_ // 7
        label = Note.TONES[tone]
        if octave > 0:
            label = label.lower()
            if octave > 1:
                label = f"${label}_{octave - 1}$"
        text(label_pos[1], label_pos[0], label,
             verticalalignment="top",
             horizontalalignment="center",
             bbox=LABEL_BBOX)
