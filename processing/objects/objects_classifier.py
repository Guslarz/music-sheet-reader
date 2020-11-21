from __future__ import annotations

from base.processor import Processor
from base.musical_object import Clef, Note, MusicalObject
from utils.data import LineData, SelectedObjectData
from utils.bbox import BBox
from config import DebugLevel

from numpy import array, arange
from enum import Enum
from skimage.draw import disk
from skimage.transform import hough_circle, hough_circle_peaks


class ObjectsClassifier(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_music_objects(self, data: list[LineData]) -> list[MusicalObject]:
        result = [
            obj
            for line in data
            for obj in self.process_single_line_(line)
        ]

        if self.debug_level >= DebugLevel.ALL:
            for obj in result:
                print(obj)

        return result

    def process_single_line_(self, data: LineData) -> list[MusicalObject]:
        first, *rest = data.objects
        clef = self.classify_clef(first)
        result = [
            clef,
            *[self.classify_note(note, clef.type) for note in rest]
        ]

        return result

    def classify_clef(self, data: SelectedObjectData) -> Clef:
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

    def classify_note(self, data: SelectedObjectData, clef_type: Enum) -> Note:
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
        r, c = disk((cy, cx), radius,
                    shape=data.img.shape)
        selected = data.img[r, c]
        white_perc = sum(selected == 1) / len(selected)

        note_width = data.img.shape[1]
        note_height = data.img.shape[0]
        if note_height < 2 * data.line.line_spacing:
            note_type = Note.Type.WHOLE_NOTE
        else:
            if white_perc < .7:
                note_type = Note.Type.HALF_NOTE
            else:
                if note_width > 2 * data.line.line_spacing:
                    note_type = Note.Type.EIGHTH_NOTE
                else:
                    note_type = Note.Type.QUARTER_NOTE

        tone = self.get_tone_(data.line, clef_type, center)

        return Note(note_type, tone, order=order,
                    line_selection=line_selection,
                    global_selection=global_selection)

    def get_tone_(self, data: LineData, clef_type: Enum, center: array) -> int:
        if clef_type == Clef.Type.G_CLEF:
            c_height = data.staff_lines[4][0][0] + data.line_spacing
        else:
            c_height = data.staff_lines[2][0][0] + data.line_spacing / 2
        tone = round(2.0 * (c_height - center[0]) / (data.line_spacing + data.line_width / 2) + 7) % 7
        return tone
