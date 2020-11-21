from __future__ import annotations

from base.processor import Processor
from utils.data import LineData
from utils.debug_saver import DebugSaver
from config import DebugLevel

from matplotlib.pyplot import subplots


class StaffLinesRemover(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'erased': DebugSaver('erased_staff_lines')
        }

    def get_lines_data(self, data: list[LineData]) -> list[LineData]:
        result = [*map(self.process_single_line_, data)]

        if self.debug_level >= DebugLevel.REPORT:
            _, axes = subplots(nrows=len(result))
            for ax, res in zip(axes, result):
                ax.imshow(res.img, cmap="gray")
            self.savers_['erased'].save(data[0].name)

        return result

    def process_single_line_(self, data: LineData) -> LineData:
        image = data.img.copy()
        margin = 2

        for staff_line in data.staff_lines:
            for i in range(image.shape[1]):
                expected_height = staff_line[i, 0]
                possibilities = [expected_height + sign * value
                                 for sign in [-1, 1]
                                 for value in range(data.line_width + margin + 1)]
                possibilities = [x for x in possibilities
                                 if image[x, i] == 1]
                if len(possibilities) == 0:
                    continue
                height = possibilities[0]
                indices = []
                j = height
                while j >= 0 and image[j, i]:
                    indices.append(j)
                    j -= 1
                j = height + 1
                while j < image.shape[0] and image[j, i]:
                    indices.append(j)
                    j += 1
                if len(indices) < 3 * data.line_width:
                    image[indices, i] = 0

        if self.debug_level >= DebugLevel.ALL:
            print("Staff lines erased")

        return LineData.from_other(data, image)

