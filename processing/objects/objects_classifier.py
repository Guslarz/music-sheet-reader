from __future__ import annotations

from base.processor import Processor
from base.musical_object import Clef, Note, MusicalObject
from utils.data import LineData, SelectedObjectData
from utils.bbox import BBox
from config import DebugLevel


class ObjectsClassifier(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_music_objects(self, data: list[LineData]) -> list[MusicalObject]:
        result = [
            obj
            for line in data
            for obj in self.process_single_line_(line)
        ]

        if self.debug_level >= DebugLevel.MAIN:
            for obj in result:
                print(obj)

        return result

    def process_single_line_(self, data: LineData) -> list[MusicalObject]:
        first, *rest = data.objects
        result = [
            self.classify_clef(first),
            *map(self.classify_note, rest)
        ]

        return result

    def classify_clef(self, data: SelectedObjectData) -> Clef:
        selection = BBox.from_image(data.img).to_points()
        line_selection = data.line_transformation\
            .apply_to_points(selection)
        global_selection = data.global_transformation\
            .apply_to_points(selection)

        order = data.order

        clef_type = Clef.Type.F_CLEF

        return Clef(clef_type, order=order,
                    line_selection=line_selection,
                    global_selection=global_selection)

    def classify_note(self, data: SelectedObjectData) -> Note:
        selection = BBox.from_image(data.img).to_points()
        line_selection = data.line_transformation\
            .apply_to_points(selection)
        global_selection = data.global_transformation\
            .apply_to_points(selection)

        order = data.order

        note_type = Note.Type.WHOLE_NOTE

        tone = 0

        return Note(note_type, tone, order=order,
                    line_selection=line_selection,
                    global_selection=global_selection)
