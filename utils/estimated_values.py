class CommonEstimatedValues(object):
    def __init__(self, line_width: int, line_spacing: int):
        self.line_width_ = line_width
        self.line_spacing_ = line_spacing

    @property
    def line_width(self):
        return self.line_width_

    @property
    def line_spacing(self):
        return self.line_spacing_


class LineEstimatedValues(object):
    def __init__(self, staff_lines):
        self.staff_lines_ = staff_lines

    @property
    def staff_lines(self):
        return self.staff_lines_
