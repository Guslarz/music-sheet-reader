from __future__ import annotations

from numpy import array


class Transformation(object):
    def __init__(self, offset: array, center: array,
                 angle: float, parent: Transformation = None):
        self.offset_ = offset
        self.center_ = center
        self.angle_ = angle
        self.parent_ = parent

    def apply_to_points(self, points: array) -> array:
        pass
