from __future__ import annotations

from numpy import array, floor, ceil, min, max


class BBox:
    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float):
        self.min_x_ = min_x
        self.min_y_ = min_y
        self.max_x_ = max_x
        self.max_y_ = max_y

    @property
    def min_x(self) -> float:
        return self.min_x_

    @property
    def min_y(self) -> float:
        return self.min_y_

    @property
    def max_x(self) -> float:
        return self.max_x_

    @property
    def max_y(self) -> float:
        return self.max_y_

    def to_points(self) -> array:
        return array([
            [self.min_y_, self.min_x_],
            [self.min_y_, self.max_x_],
            [self.max_y_, self.max_x_],
            [self.max_y_, self.min_x_],
            [self.min_y_, self.min_x_]
        ])

    @staticmethod
    def from_contour(contour: array) -> BBox:
        return BBox(
            floor(min(contour[:, 1])),
            floor(min(contour[:, 0])),
            ceil(max(contour[:, 1])),
            ceil(max(contour[:, 0]))
        )
