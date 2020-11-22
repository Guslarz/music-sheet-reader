from __future__ import annotations

from base.processor import Processor
from utils.data import TransformedImageData
from utils.debug_saver import DebugSaver
from utils.bbox import BBox
from utils.transformation import Translation
from config import DebugLevel

from skimage.filters import sobel
from skimage.morphology import closing, erosion, \
    dilation, remove_small_objects, disk
from skimage.feature import canny, corner_peaks, corner_harris
from matplotlib.pyplot import imshow, plot
from numpy import array
from scipy.ndimage import binary_fill_holes


class SheetExtractor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'edge': DebugSaver('sheet_edge'),
            'corners': DebugSaver('sheet_corners'),
            'cropped': DebugSaver('sheet_cropped'),
            'on-initial': DebugSaver('sheet_on_initial')
        }

    def get_sheet_data(self, data: TransformedImageData) -> TransformedImageData:
        edge = self.get_edge_(data)
        bbox = self.get_bbox_(data, edge)
        cropped = bbox.crop_image(data.img)

        translation = Translation(bbox.offset,
                                  parent=data.transformation)

        if self.debug_level >= DebugLevel.MAIN:
            imshow(data.initial_img)
            points = BBox.from_image(cropped).to_points()
            points = translation.apply_to_points(points)
            plot(points[:, 1], points[:, 0])
            self.savers_['on-initial'].save(data.name)

        if self.debug_level >= DebugLevel.REPORT:
            imshow(cropped, cmap="gray")
            self.savers_['cropped'].save(data.name)

        return TransformedImageData(data.raw_data,
                                    cropped, translation)

    def get_edge_(self, data: TransformedImageData) -> array:
        image = data.img
        image = image ** 2
        image = canny(image, sigma=2)
        image = dilation(image)
        image = closing(image)
        image = binary_fill_holes(image)
        image = erosion(image, disk(3))
        image = remove_small_objects(image, 5000)
        image = sobel(image)

        if self.debug_level >= DebugLevel.ALL:
            imshow(image, cmap="gray")
            self.savers_['edge'].save(data.name)

        return image

    def get_bbox_(self, data: TransformedImageData,
                  image: array) -> BBox:
        coords = corner_peaks(corner_harris(image),
                              threshold_rel=0,
                              num_peaks=4)
        x_values = sorted(coords[:, 1])
        y_values = sorted(coords[:, 0])
        min_x, max_x = x_values[1:3]
        min_y, max_y = y_values[1:3]

        if self.debug_level >= DebugLevel.REPORT:
            imshow(image, cmap="gray")
            plot(coords[:, 1], coords[:, 0], '+r',
                 markersize=15)
            self.savers_['corners'].save(data.name)

        return BBox(min_x, min_y, max_x, max_y)
