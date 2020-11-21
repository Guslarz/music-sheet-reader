from __future__ import annotations

from base.processor import Processor
from utils.data import TransformedImageData
from utils.transformation import Translation
from utils.debug_saver import DebugSaver
from utils.bbox import BBox
from config import DebugLevel

from skimage.feature import canny
from skimage.morphology import closing, dilation, \
    remove_small_objects
from skimage.measure import find_contours
from scipy.ndimage import binary_fill_holes
from numpy import array
from matplotlib.pyplot import imshow, plot, subplots


class LineExtractor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'enhanced': DebugSaver('line_ex_enhanced'),
            'contours': DebugSaver('line_ex_contours'),
            'cropped': DebugSaver('line_ex_cropped'),
            'on-initial': DebugSaver('line_ex_on_initial')
        }

    def get_lines_data(self, data: TransformedImageData) -> list[TransformedImageData]:
        enhanced = self.get_enhanced_image_(data)
        bounding_boxes = self.get_line_bounding_boxes_(data, enhanced)

        result = []
        for bbox in bounding_boxes:
            cropped = bbox.crop_image(data.img)
            if any(dim < 20 for dim in cropped.shape):
                continue
            translation = Translation(bbox.offset,
                                      parent=data.transformation)
            new_data = TransformedImageData(data.raw_data,
                                            cropped, translation)
            result.append(new_data)

        if self.debug_level >= DebugLevel.MAIN:
            _, axes = subplots(nrows=len(result))
            for ax, res in zip(axes, result):
                ax.imshow(res.img, cmap="gray")
            self.savers_['cropped'].save(data.name)

        if self.debug_level >= DebugLevel.MAIN:
            imshow(data.initial_img)
            for res in result:
                bbox = BBox.from_image(res.img)
                points = bbox.to_points()
                points = res.transformation.apply_to_points(points)
                plot(points[:, 1], points[:, 0])
            self.savers_['on-initial'].save(data.name)

        return result

    def get_enhanced_image_(self, data: TransformedImageData) -> array:
        image = canny(data.img)
        image = closing(image)
        image = dilation(image)
        image = binary_fill_holes(image)
        image = remove_small_objects(image, 500)
        image = dilation(image)

        if self.debug_level >= DebugLevel.ALL:
            imshow(image, cmap="gray")
            self.savers_['enhanced'].save(data.name)

        return image

    def get_line_bounding_boxes_(self, data: TransformedImageData, image: array) -> list[BBox]:
        contours = find_contours(image, .5)

        if self.debug_level >= DebugLevel.REPORT:
            imshow(image, cmap="gray")
            for contour in contours:
                plot(contour[:, 1], contour[:, 0])
            self.savers_['contours'].save(data.name)

        bounding_boxes = [*map(BBox.from_contour, contours)]
        return bounding_boxes
