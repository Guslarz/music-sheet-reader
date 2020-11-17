from input.raw_data import RawData
from utils.transformation import Transformation

from numpy import array


class SheetData:
    def __init__(self, raw_data: RawData, sheet: array,
                 transformation: Transformation):
        self.raw_data_ = raw_data
        self.sheet_ = sheet
        self.transformation_ = transformation

    @property
    def raw_data(self):
        return self.raw_data_

    @property
    def name(self):
        return self.raw_data_.name

    @property
    def initial_img(self):
        return self.raw_data_.img

    @property
    def sheet(self):
        return self.sheet_

    @property
    def transformation(self):
        return self.transformation_
