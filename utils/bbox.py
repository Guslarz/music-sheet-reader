from __future__ import annotations

from numpy import array, floor, ceil, min as npmin, max as npmax


class BBox:
    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float):
        self.min_x_ = int(min_x)
        self.min_y_ = int(min_y)
        self.max_x_ = int(max_x)
        self.max_y_ = int(max_y)

    @property
    def min_x(self) -> float:
        return self.min_x_

    @min_x.setter
    def min_x(self, value):
        self.min_x_ = value

    @property
    def min_y(self) -> float:
        return self.min_y_

    @min_y.setter
    def min_y(self, value):
        self.min_y_ = value

    @property
    def max_x(self) -> float:
        return self.max_x_

    @max_x.setter
    def max_x(self, value):
        self.max_x_ = value

    @property
    def max_y(self) -> float:
        return self.max_y_

    @max_y.setter
    def max_y(self, value):
        self.max_y_ = value

    @property
    def offset(self) -> array:
        return array((self.min_y, self.min_x))

    def to_points(self) -> array:
        return array([
            [self.min_y_, self.min_x_],
            [self.min_y_, self.max_x_],
            [self.max_y_, self.max_x_],
            [self.max_y_, self.min_x_],
            [self.min_y_, self.min_x_]
        ])

    def crop_image(self, image: array) -> array:
        return image[
               self.min_y:(self.max_y + 1),
               self.min_x:(self.max_x + 1)]

    @staticmethod
    def from_contour(contour: array) -> BBox:
        return BBox(
            floor(npmin(contour[:, 1])),
            floor(npmin(contour[:, 0])),
            ceil(npmax(contour[:, 1])),
            ceil(npmax(contour[:, 0]))
        )

    @staticmethod
    def from_image(image: array) -> BBox:
        return BBox(0, 0, *image.shape[::-1])

    @staticmethod
    def merge(a: BBox, b: BBox) -> BBox:
        return BBox(
            min(a.min_x, b.min_x),
            min(a.min_y, b.min_y),
            max(a.max_x, b.max_x),
            max(a.max_y, b.max_y)
        )
