from __future__ import annotations

from base.musical_object import MusicalObject
from config import SAVE, OUT_DIR, OUT_EXT

from numpy import array
from matplotlib.pyplot import imshow, plot, show, savefig


class Result(object):
    def __init__(self, name: str, img: array, objects: list[MusicalObject]):
        self.name_ = name
        self.img_ = img
        self.objects_ = objects

    @property
    def name(self):
        return self.name_

    @property
    def img(self):
        return self.img_

    @property
    def objects(self):
        return self.objects_

    def show(self):
        imshow(self.img_)

        for obj in self.objects_:
            points = obj.global_selection
            plot(points[:, 1], points[:, 0])

        if SAVE:
            filename = f"{OUT_DIR}/output-{self.name_}.{OUT_EXT}"
            savefig(filename)
        else:
            show()
