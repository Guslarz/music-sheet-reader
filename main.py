from utils.debug_saver import DebugSaver
from input.input_reader import InputReader
from processing.initial.initial_rotator import InitialRotator
from processing.sheet.sheet_extractor import SheetExtractor
from processing.line.line_extractor import LineExtractor
from processing.line.line_rotator import LineRotator
from config import DebugLevel


def main():
    # setup plots style
    DebugSaver.setup()

    # processors
    input_reader = InputReader(debug_level=DebugLevel.OFF)
    initial_rotator = InitialRotator(debug_level=DebugLevel.OFF)
    sheet_extractor = SheetExtractor(debug_level=DebugLevel.OFF)
    line_extractor = LineExtractor(debug_level=DebugLevel.OFF)
    line_rotator = LineRotator(debug_level=DebugLevel.OFF)

    # process data
    for raw_data in input_reader.get_raw_data():
        rotated_data = initial_rotator.get_rotated_data(raw_data)
        sheet_data = sheet_extractor.get_sheet_data(rotated_data)
        lines_data = line_extractor.get_lines_data(sheet_data)
        lines_data = line_rotator.get_lines_data(lines_data)


if __name__ == '__main__':
    main()
