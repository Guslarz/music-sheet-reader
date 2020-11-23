from __future__ import annotations

from base.processor import Processor
from base.musical_object import Clef, Note, MusicalObject
from utils.data import LineData, SelectedObjectData
from utils.bbox import BBox
from utils.debug_saver import DebugSaver
from config import DebugLevel

from skimage.draw import disk
from skimage.transform import hough_circle, hough_circle_peaks
from numpy import array, arange
from enum import Enum
from matplotlib.pyplot import subplots
from matplotlib.axes import Axes


class ObjectsClassifier(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'centers': DebugSaver('classifier-centers')
        }

    def get_music_objects(self, data: list[LineData]) -> list[MusicalObject]:
        if self.debug_level >= DebugLevel.REPORT:
            _, axes = subplots(nrows=len(data))
        else:
            axes = [None for _ in data]

        result = [
            obj
            for ax, line in zip(axes, data)
            for obj in self.process_single_line_(line, ax)
        ]

        if self.debug_level >= DebugLevel.REPORT:
            self.savers_['centers'].save(data[0].name)

        return result

    def process_single_line_(self, data: LineData, ax: Axes) -> list[MusicalObject]:
        if self.debug_level >= DebugLevel.REPORT:
            ax.imshow(data.img, cmap="gray")

        first, *rest = data.objects
        clef = self.classify_clef_(first)
        result = [
            clef,
            *[self.classify_note_(note, clef.type, ax) for note in rest]
        ]

        return result

    def classify_clef_(self, data: SelectedObjectData) -> Clef:
        selection = BBox.from_image(data.img).to_points()
        line_selection = data.line_transformation\
            .apply_to_points(selection)
        global_selection = data.global_transformation\
            .apply_to_points(selection)

        order = data.order

        clef_type = Clef.Type.F_CLEF if \
            data.img.shape[0] < data.line.line_spacing * 5 \
            else Clef.Type.G_CLEF

        return Clef(clef_type, order=order,
                    line_selection=line_selection,
                    global_selection=global_selection)

    def classify_note_(self, data: SelectedObjectData, clef_type: Enum, ax: Axes) -> Note:
        selection = BBox.from_image(data.img).to_points()
        line_selection = data.line_transformation\
            .apply_to_points(selection)
        global_selection = data.global_transformation\
            .apply_to_points(selection)

        order = data.order

        hough_radii = arange(data.line.line_spacing // 2,
                             data.line.line_spacing * 2, 1)
        hough_res = hough_circle(data.img, hough_radii)
        _, cx, cy, radius = [*zip(*hough_circle_peaks(hough_res, hough_radii,
                                                      total_num_peaks=1))][0]

        center = data.line_transformation\
            .apply_to_points(array([[cy, cx]]))[0]

        if self.debug_level >= DebugLevel.REPORT:
            ax.plot(center[1], center[0], 'ro')

        r, c = disk((cy, cx), radius,
                    shape=data.img.shape)
        selected = data.img[r, c]
        if len(selected) == 0:
            white_perc = 0
        else:
            white_perc = sum(selected == 1) / len(selected)

        note_height = data.img.shape[0]
        if note_height < 2 * data.line.line_spacing:
            note_type = Note.Type.WHOLE_NOTE
        else:
            if white_perc < .7:
                note_type = Note.Type.HALF_NOTE
            else:
                half_height = note_height // 2
                half = data.img[:half_height, :] if cy >= half_height else data.img[half_height:, :]
                if not (half == 1).any():
                    note_type = Note.Type.QUARTER_NOTE
                else:
                    left = 0
                    while not (half[:, left]).any():
                        left += 1
                    right = half.shape[1] - 1
                    while not (half[:, right]).any():
                        right -= 1
                    width = right - left + 1
                    note_type = Note.Type.EIGHTH_NOTE if width > 3 * data.line.line_width else Note.Type.QUARTER_NOTE

        tone = self.get_tone_(data.line, clef_type, center)

        return Note(note_type, tone, order=order,
                    line_selection=line_selection,
                    global_selection=global_selection)

    def get_tone_(self, data: LineData, clef_type: Enum, center: array) -> int:
        if clef_type == Clef.Type.G_CLEF:
            c_height = data.staff_lines[4][0][0] + data.line_spacing
            octave = 2
        else:
            c_height = data.staff_lines[2][0][0] + data.line_spacing / 2
            octave = 1
        tone = round(2.0 * (c_height - center[0]) / (data.line_spacing + data.line_width / 2) + 7 * octave)
        return tone
