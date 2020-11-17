from __future__ import annotations

from numpy import array, sin, cos, dot


class Transformation(object):
    def __init__(self, parent: Transformation = None):
        self.parent_ = parent

    def apply_to_points(self, points: array) -> array:
        points = self.inner_apply_to_points_(points)
        if self.parent_:
            points = self.parent_.apply_to_points(points)
        return points

    def inner_apply_to_points_(self, points: array) -> array:
        pass

class Translation(Transformation):
    def __init__(self, offset: array, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset_ = offset

    def inner_apply_to_points_(self, points: array) -> array:
        return points + self.offset_


class Rotation(Transformation):
    def __init__(self, angle: float, center: array,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.center_ = center
        angle = angle
        self.rotation_matrix_ = array([
            [cos(angle),
             -sin(angle)],
            [sin(angle),
             cos(angle)]
        ])

    def inner_apply_to_points_(self, points: array) -> array:
        points = points - self.center_
        points = dot(points, self.rotation_matrix_)
        points = points + self.center_
        return points
