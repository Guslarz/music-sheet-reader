from utils.debug_saver import DebugSaver
from input.input_reader import InputReader


def main():
    # setup plots style
    DebugSaver.setup()

    # processors
    input_reader = InputReader()

    # read data
    for raw_data in input_reader.get_raw_data():
        print(raw_data.name)


if __name__ == '__main__':
    main()
