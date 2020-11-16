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
