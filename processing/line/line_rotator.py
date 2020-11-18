from __future__ import annotations

from base.processor import Processor
from utils.data import TransformedImageData
from utils.transformation import Rotation
from utils.functions import threshold, contrast
from utils.debug_saver import DebugSaver
from utils.bbox import BBox
from config import DebugLevel

from skimage.filters import threshold_otsu
from skimage.transform import hough_line, hough_line_peaks
from numpy import array, linspace, pi, cos, sin, mean
from matplotlib.pyplot import imshow, plot, subplots
from scipy.ndimage import rotate


class LineRotator(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'enhanced': DebugSaver('line_rot_enhanced'),
            'hough-lines': DebugSaver('line_rot_hough_lines'),
            'single-rotated': DebugSaver('line_rot_single_rot'),
            'result': DebugSaver('line_rot_result'),
            'on-initial': DebugSaver('line_rot_on_initial')
        }

    def get_lines_data(self, data: list[TransformedImageData]) -> list[TransformedImageData]:
        result = [*map(self.process_single_line_, data)]
        raw_data = data[0].raw_data

        if self.debug_level >= DebugLevel.MAIN:
            _, axes = subplots(nrows=len(result))
            for ax, res in zip(axes, result):
                ax.imshow(res.img, cmap="gray")
            self.savers_['result'].save(raw_data.name)

        if self.debug_level >= DebugLevel.MAIN:
            imshow(raw_data.img)
            for res in result:
                bbox = BBox.from_image(res.img)
                points = bbox.to_points()
                points = res.transformation.apply_to_points(points)
                plot(points[:, 1], points[:, 0])
            self.savers_['on-initial'].save(raw_data.name)

        return result

    def process_single_line_(self, data: TransformedImageData) -> TransformedImageData:
        enhanced = self.get_enhanced_image_(data)
        angles = self.get_angles_(data, enhanced)

        rotation_angle = mean(angles) - pi / 2
        rotation_deg = rotation_angle * 180 / pi
        rotated = rotate(data.img, rotation_deg,
                         reshape=False, mode="nearest")
        rotation = Rotation(rotation_angle,
                            Rotation.center_from_img(data.img),
                            parent=data.transformation)

        if self.debug_level >= DebugLevel.ALL:
            imshow(rotated, cmap="gray")
            self.savers_['single-rotated'].save(data.name)

        return TransformedImageData(data.raw_data, rotated,
                                    rotation)

    def get_enhanced_image_(self, data: TransformedImageData) -> array:
        image = data.img ** 2
        image = contrast(image, 0, 30)
        image = 1 - image
        image = threshold(image, threshold_otsu(image))

        if self.debug_level >= DebugLevel.ALL:
            imshow(image, cmap="gray")
            self.savers_['enhanced'].save(data.name)

        return image

    def get_angles_(self, data: TransformedImageData, img: array) -> array:
        tested_angles = linspace(pi / 2 - pi / 45,
                                 pi / 2 + pi / 45, 60)
        h, theta, d = hough_line(img, theta=tested_angles)
        _, angles, dists = hough_line_peaks(h, theta, d,
                                            num_peaks=5,
                                            min_distance=2)

        if self.debug_level >= DebugLevel.MAIN:
            origin = array((0, img.shape[1] - 1))
            imshow(img, cmap="gray")
            for angle, dist in zip(angles, dists):
                y0, y1 = (dist - origin * cos(angle)) / \
                         sin(angle)
                plot(origin, (y0, y1), 'r-')
            self.savers_['hough-lines'].save(data.name)

        return angles

