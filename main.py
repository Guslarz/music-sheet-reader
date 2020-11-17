from utils.debug_saver import DebugSaver
from input.input_reader import InputReader
from processing.initial.initial_rotator import InitialRotator
from processing.sheet.sheet_extractor import SheetExtractor
from processing.line.line_extractor import LineExtractor
from processing.line.line_rotator import LineRotator
from processing.line.line_binarizer import LineBinarizer
from processing.line.line_estimator import LineEstimator
from processing.line.staff_lines_remover import StaffLinesRemover
from processing.objects.objects_selector import ObjectsSelector
from processing.objects.objects_classifier import ObjectsClassifier
from base.result import Result
from config import DebugLevel


def main():
    # setup plots style and output dir
    DebugSaver.setup()

    # processors
    input_reader = InputReader(debug_level=DebugLevel.OFF)
    initial_rotator = InitialRotator(debug_level=DebugLevel.OFF)
    sheet_extractor = SheetExtractor(debug_level=DebugLevel.OFF)
    line_extractor = LineExtractor(debug_level=DebugLevel.OFF)
    line_rotator = LineRotator(debug_level=DebugLevel.OFF)
    line_binarizer = LineBinarizer(debug_level=DebugLevel.OFF)
    line_estimator = LineEstimator(debug_level=DebugLevel.OFF)
    staff_lines_remover = StaffLinesRemover(debug_level=DebugLevel.OFF)
    objects_selector = ObjectsSelector(debug_level=DebugLevel.OFF)
    objects_classifier = ObjectsClassifier(debug_level=DebugLevel.OFF)

    # process data
    for raw_data in input_reader.get_raw_data():
        rotated_data = initial_rotator.get_rotated_data(raw_data)
        sheet_data = sheet_extractor.get_sheet_data(rotated_data)
        lines_data = line_extractor.get_lines_data(sheet_data)
        lines_data = line_rotator.get_lines_data(lines_data)
        lines_data = line_binarizer.get_lines_data(lines_data)
        lines_data = line_estimator.get_lines_data(lines_data)
        lines_data = staff_lines_remover.get_lines_data(lines_data)
        objects_selector.get_objects_data(lines_data)
        musical_objects = objects_classifier.get_music_objects(lines_data)
        result = Result(raw_data.name, raw_data.img, musical_objects)
        result.show()


if __name__ == '__main__':
    main()
