from __future__ import annotations

from base.processor import Processor
from utils.images_generator import ImagesGenerator
from utils.data import RawData
from utils.debug_saver import DebugSaver
from config import DebugLevel

from sys import stdin
from matplotlib import pyplot as plt
from collections.abc import Iterable


class InputReader(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'initial': DebugSaver('initial-image')
        }

    def get_raw_data(self) -> Iterable[RawData]:
        for data in ImagesGenerator(stdin):
            if self.debug_level >= DebugLevel.REPORT:
                plt.imshow(data.img)
                self.savers_['initial'].save(data.name)

            yield data
