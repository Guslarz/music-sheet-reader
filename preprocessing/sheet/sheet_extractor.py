from __future__ import annotations

from base.processor import Processor
from input.raw_data import RawData
from utils.debug_saver import DebugSaver
from preprocessing.sheet.sheet_data import SheetData
from utils.functions import threshold
from utils.bbox import BBox
from utils.transformation import Rotation, Translation
from config import DebugLevel

from skimage.color import rgb2gray
from skimage.filters import sobel, threshold_otsu
from skimage.morphology import closing, erosion
from skimage.transform import hough_line, hough_line_peaks
from skimage.feature import canny, corner_peaks, corner_harris
from matplotlib.pyplot import imshow, plot
from numpy import array, linspace, pi, amax, cos, sin, median
from scipy.ndimage import rotate, binary_fill_holes


class SheetExtractor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gray_saver_ = DebugSaver('gray')
        self.rotation_enhanced_saver_ = DebugSaver('rotation_enhanced')
        self.rotated_saver_ = DebugSaver('rotated')
        self.sheet_edge_saver_ = DebugSaver('sheet_edge')
        self.sheet_corners_saver_ = DebugSaver('sheet_corners')
        self.cropped_sheet_saver_ = DebugSaver('cropped_sheet')
        self.sheet_bbox_on_initial_saver_ = DebugSaver('sheet_bbox_on_initial')

    def get_sheet_data(self, raw_data: RawData) -> SheetData:
        gray = self.get_gray_(raw_data)

        angle, rotated = self.get_rotated_(raw_data, gray)
        center = array(gray.shape) / 2
        rotation = Rotation(angle, center)

        bbox, sheet = self.get_sheet_(raw_data, rotated)
        offset = array((bbox.min_y, bbox.min_x))
        translation = Translation(offset, parent=rotation)

        if self.debug_level >= DebugLevel.MAIN:
            imshow(raw_data.img)
            points = BBox.from_image(sheet).to_points()
            points = translation.apply_to_points(points)
            plot(points[:, 1], points[:, 0])
            self.sheet_bbox_on_initial_saver_.save(raw_data.name)

        return SheetData(raw_data, sheet, translation)

    def get_gray_(self, raw_data: RawData) -> array:
        img = rgb2gray(raw_data.img)

        if self.debug_level >= DebugLevel.ALL:
            imshow(img, cmap="gray")
            self.gray_saver_.save(raw_data.name)

        return img

    def get_rotated_(self, raw_data: RawData, gray: array) -> \
            tuple[float, array]:
        def enhance_image(image: array) -> array:
            image = sobel(image)
            image = threshold(image, threshold_otsu(image))
            image = closing(image)

            if self.debug_level >= DebugLevel.ALL:
                imshow(image, cmap="gray")
                self.rotation_enhanced_saver_\
                    .save(raw_data.name)

            return image

        def find_angles(image: array) -> array:
            tested_angles = linspace(pi / 4, 3 * pi / 4, 360)
            h, theta, d = hough_line(image,
                                     theta=tested_angles)
            _, angles, dists = \
                hough_line_peaks(h, theta, d,
                                 threshold=.8 * amax(h),
                                 min_distance=2)

            if self.debug_level >= DebugLevel.ALL:
                imshow(image, cmap="gray")
                origin = array((0, image.shape[1] - 1))
                for angle, dist in zip(angles, dists):
                    y0, y1 = (dist - origin * cos(angle)) / \
                             sin(angle)
                    plot(origin, (y0, y1), 'r-')

            return angles

        enhanced = enhance_image(gray)
        rotation_angle = median(find_angles(enhanced)) - pi / 2
        rotated = rotate(gray, rotation_angle * 180 / pi,
                         reshape=False, mode="nearest")

        if self.debug_level >= DebugLevel.MAIN:
            imshow(rotated, cmap="gray")
            self.rotated_saver_.save(raw_data.name)

        return rotation_angle, rotated

    def get_sheet_(self, raw_data: RawData, rotated: array) -> \
            tuple[BBox, array]:
        def find_edge(image: array) -> array:
            image = canny(image, sigma=2)
            image = closing(image)
            image = binary_fill_holes(image)
            image = erosion(image)
            image = sobel(image)

            if self.debug_level >= DebugLevel.ALL:
                imshow(image, cmap="gray")
                self.sheet_edge_saver_.save(raw_data.name)

            return image

        def get_bbox(image: array) -> BBox:
            coords = corner_peaks(corner_harris(image),
                                  threshold_rel=0,
                                  num_peaks=4)
            x_values = sorted(coords[:, 1])
            y_values = sorted(coords[:, 0])
            min_x, max_x = x_values[1:3]
            min_y, max_y = y_values[1:3]

            if self.debug_level >= DebugLevel.ALL:
                imshow(rotated, cmap="gray")
                plot(coords[:, 1], coords[:, 0], '+r',
                     markersize=15)
                self.sheet_corners_saver_\
                    .save(raw_data.name)

            return BBox(min_x, min_y, max_x, max_y)

        edge = find_edge(rotated)
        bbox = get_bbox(edge)
        cropped = rotated[
                    bbox.min_y:bbox.max_y,
                    bbox.min_x:bbox.max_x]

        if self.debug_level >= DebugLevel.MAIN:
            imshow(cropped, cmap="gray")
            self.cropped_sheet_saver_.save(raw_data.name)

        return bbox, cropped
