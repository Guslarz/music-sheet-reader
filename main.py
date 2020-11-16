from utils.debug_saver import DebugSaver
from input.input_reader import InputReader
from preprocessing.sheet_extractor import SheetExtractor
from config import DebugLevel


def main():
    # setup plots style
    DebugSaver.setup()

    # processors
    input_reader = InputReader(debug_level=DebugLevel.OFF)
    sheet_extractor = SheetExtractor(debug_level=DebugLevel.OFF)

    # read data
    for raw_data in input_reader.get_raw_data():
        sheet_data = sheet_extractor.get_sheet_data(raw_data)


if __name__ == '__main__':
    main()
