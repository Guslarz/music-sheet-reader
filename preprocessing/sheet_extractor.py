from base.processor import Processor
from input.raw_data import RawData


class SheetExtractor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def extract_sheet(self, raw_data: RawData):
        pass
