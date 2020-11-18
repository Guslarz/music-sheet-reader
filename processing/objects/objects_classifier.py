from __future__ import annotations

from base.processor import Processor
from base.musical_object import Clef, Note, MusicalObject
from utils.data import LineData, SelectedObjectData
from utils.bbox import BBox
from config import DebugLevel

from numpy import array
from enum import Enum


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

        note_width = data.img.shape[1]
        note_height = data.img.shape[0]
        if note_height < 2 * data.line.line_spacing:
            note_type = Note.Type.WHOLE_NOTE
            center = data.line_transformation.apply_to_points([
                array((note_height, note_width)) / 2
            ])[0]
        else:
            blacks = data.img.sum(axis=1)
            if sum(blacks > data.line.line_spacing) < 3 * data.line.line_width:
                note_type = Note.Type.HALF_NOTE
            else:
                if note_width > 2 * data.line.line_spacing:
                    note_type = Note.Type.EIGHTH_NOTE
                else:
                    note_type = Note.Type.QUARTER_NOTE

            y0 = int(data.line.line_spacing / 2)
            y1 = int(note_height - data.line.line_spacing / 2)
            if blacks[y0] > blacks[y1]:
                center = array((y0, note_width / 2))
            else:
                center = array((y1, note_width / 2))
            center = data.line_transformation.apply_to_points([center])[0]

        tone = self.get_tone(data.line, clef_type, center)

        return Note(note_type, tone, order=order,
                    line_selection=line_selection,
                    global_selection=global_selection)

    def get_tone(self, data: LineData, clef_type: Enum, center: array) -> int:
        if clef_type == Clef.Type.G_CLEF:
            c_height = data.staff_lines[4][0][0] + data.line_spacing
        else:
            c_height = data.staff_lines[2][0][0] + data.line_spacing / 2
        tone = round(2.0 * (c_height - center[0]) / (data.line_spacing + data.line_width / 2) + 7) % 7
        return tone
