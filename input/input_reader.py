from __future__ import annotations

from base.processor import Processor
from input.images_generator import ImagesGenerator
from input.raw_data import RawData
from utils.debug_saver import DebugSaver
from config import DebugLevel

from sys import stdin
from matplotlib import pyplot as plt
from collections.abc import Iterable


class InputReader(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_image_saver_ = DebugSaver('initial-image')

    def get_raw_data(self) -> Iterable[RawData]:
        for data in ImagesGenerator(stdin):
            if self.debug_level >= DebugLevel.MAIN:
                plt.imshow(data.img)
                self.initial_image_saver_.save(data.name)

            yield data
