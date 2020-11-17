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

        if self.debug_level >= DebugLevel.MAIN:
            _, axes = subplots(nrows=len(result))
            for ax, res in zip(axes, result):
                ax.imshow(res.img, cmap="gray")
            self.savers_['erased'].save(data[0].name)

        return result

    def process_single_line_(self, data: LineData) -> LineData:
        image = data.img.copy()
        margin = 1

        for staff_line in data.staff_lines:
            for i in range(image.shape[1]):
                height = staff_line[i, 0]
                image[(height - data.line_width - margin):height, i] = \
                    image[(height - data.line_width - margin - 1), i]
                image[height:(height + data.line_width + margin + 1), i] = \
                    image[(height + data.line_width + margin + 1), i]

        if self.debug_level >= DebugLevel.ALL:
            print("Staff lines erased")

        return LineData.from_other(data, image)

