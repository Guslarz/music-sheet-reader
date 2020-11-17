from __future__ import annotations

from utils.transformation import Transformation
from utils.estimated_values import CommonEstimatedValues, \
    LineEstimatedValues

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


class LineData(object):
    def __init__(self, image_data: TransformedImageData,
                 common_values: CommonEstimatedValues,
                 values: LineEstimatedValues):
        self.image_data_ = image_data
        self.common_ = common_values
        self.values_ = values
        self.objects_ = []
        self.height_ = image_data.transformation\
            .apply_to_points(array([[0, 0]]))[0][0]

    @property
    def raw_data(self):
        return self.image_data_.raw_data

    @property
    def name(self):
        return self.image_data_.name

    @property
    def initial_img(self):
        return self.image_data_.initial_img

    @property
    def img(self):
        return self.image_data_.img

    @property
    def transformation(self):
        return self.image_data_.transformation

    @property
    def common_values(self):
        return self.common_

    @property
    def line_width(self):
        return self.common_.line_width

    @property
    def line_spacing(self):
        return self.common_.line_spacing

    @property
    def values(self):
        return self.values_

    @property
    def staff_lines(self):
        return self.values_.staff_lines

    @property
    def objects(self):
        return self.objects_

    @property
    def height(self):
        return self.height_

    def add_object(self, obj: SelectedObjectData):
        self.objects_.append(obj)

    @staticmethod
    def from_other(other: LineData, image: array):
        image_data = TransformedImageData(other.raw_data,
                                          image,
                                          other.transformation)
        return LineData(image_data, other.common_values, other.values)


class SelectedObjectData(object):
    def __init__(self, line: LineData, img: array,
                 line_transformation: Transformation,
                 global_transformation: Transformation):
        self.line_ = line
        line.add_object(self)
        self.img_ = img
        self.line_transformation_ = line_transformation
        self.global_transformation_ = global_transformation
        self.order_ = None
        self.line_order_ = None

    @property
    def line(self):
        return self.line_

    @property
    def img(self):
        return self.img_

    @property
    def line_transformation(self):
        return self.line_transformation_

    @property
    def global_transformation(self):
        return self.global_transformation_

    @property
    def order(self):
        return self.order_

    @order.setter
    def order(self, value):
        self.order_ = value

    @property
    def line_order(self):
        return self.line_order_

    @order.setter
    def line_order(self, value):
        self.line_order_ = value

    @property
    def offset_x(self):
        return self.line_transformation_\
            .apply_to_points([[0, 0]])[0][1]
