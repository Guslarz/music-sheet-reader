from __future__ import annotations

from base.processor import Processor
from utils.data import TransformedImageData
from utils.debug_saver import DebugSaver
from utils.functions import threshold, contrast
from config import DebugLevel

from skimage.filters import threshold_otsu
from matplotlib.pyplot import imshow, subplots


class LineBinarizer(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'single': DebugSaver('line_bin_single'),
            'result': DebugSaver('line_bin_result')
        }

    def get_lines_data(self, data: list[TransformedImageData]) -> list[TransformedImageData]:
        result = [*map(self.process_single_line_, data)]
        raw_data = data[0].raw_data

        if self.debug_level >= DebugLevel.REPORT:
            _, axes = subplots(len(result))
            for ax, res in zip(axes, result):
                ax.imshow(res.img, cmap="gray")
            self.savers_['result'].save(raw_data.name)

        return result

    def process_single_line_(self, data: TransformedImageData) -> TransformedImageData:
        image = data.img ** 2
        image = 1 - image
        image = contrast(image, 30, 0)
        window_size = image.shape[0]
        if window_size % 2 == 0:
            window_size -= 1
        image = threshold(image, threshold_otsu(image))

        if self.debug_level >= DebugLevel.ALL:
            imshow(image, cmap="gray")
            self.savers_['single'].save(data.name)

        return TransformedImageData(data.raw_data, image,
                                    data.transformation)

