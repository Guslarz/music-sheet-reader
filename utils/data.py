from utils.transformation import Transformation

from skimage.io import imread
from numpy import array


class RawData(object):
    def __init__(self, path: str):
        self.name_ = path.split('/')[-1].split('.')[-2]
        self.img_ = imread(path, False)

    @property
    def name(self) -> str:
        return self.name_

    @property
    def img(self) -> array:
        return self.img_


class TransformedImageData(object):
    def __init__(self, raw_data: RawData, img: array,
                 transformation: Transformation):
        self.raw_data_ = raw_data
        self.img_ = img
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
    def img(self):
        return self.img_

    @property
    def transformation(self):
        return self.transformation_
