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
from base.musical_object import MusicalObject
from config import DebugLevel, TRACEBACK

from traceback import print_exception
from sys import exc_info


def main():
    # setup plots style and output dir
    DebugSaver.setup()

    # processors
    input_reader = InputReader(debug_level=DebugLevel.REPORT)
    initial_rotator = InitialRotator()
    sheet_extractor = SheetExtractor()
    line_extractor = LineExtractor()
    line_rotator = LineRotator()
    line_binarizer = LineBinarizer()
    line_estimator = LineEstimator()
    staff_lines_remover = StaffLinesRemover()
    objects_selector = ObjectsSelector()
    objects_classifier = ObjectsClassifier()

    # process data
    for raw_data in input_reader.get_raw_data():
        try:
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
        except:
            print(f"Error while processing {raw_data.name}")
            if TRACEBACK:
                print_exception(*exc_info())

    # show legend
    MusicalObject.show_legend()


if __name__ == '__main__':
    main()
