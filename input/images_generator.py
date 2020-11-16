from __future__ import annotations

from input.raw_data import RawData

from collections.abc import Iterable


class ImagesGenerator(object):
    def __init__(self, paths: Iterable[str]):
        self.it_ = paths.__iter__()

    def __iter__(self) -> Iterable[RawData]:
        return self

    def __next__(self) -> RawData:
        path = self.it_.__next__().rstrip()
        image = RawData(path)
        return image
