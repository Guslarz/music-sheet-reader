from base.processor import Processor
from utils.data import RawData, TransformedImageData
from utils.debug_saver import DebugSaver
from utils.transformation import Rotation
from utils.functions import threshold
from config import DebugLevel

from skimage.color import rgb2gray
from skimage.feature import canny
from skimage.filters import sobel, threshold_otsu
from skimage.morphology import closing
from skimage.transform import hough_line, hough_line_peaks
from numpy import array, linspace, pi, amax, sin, cos, median
from matplotlib.pyplot import imshow, plot, ylim
from scipy.ndimage import rotate


class InitialRotator(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'gray': DebugSaver('rot_gray'),
            'enhanced': DebugSaver('rot_enhanced'),
            'lines': DebugSaver('rot_hough_lines'),
            'result': DebugSaver('rot_result')
        }

    def get_rotated_data(self, raw_data: RawData) -> TransformedImageData:
        gray = self.get_gray_(raw_data)
        enhanced = self.get_enhanced_image_(raw_data, gray)
        angles = self.get_angles_(raw_data, enhanced)

        rotation_angle = median(angles) - pi / 2
        rotation_deg = rotation_angle * 180 / pi
        rotated = rotate(gray, rotation_deg, reshape=False,
                         mode="nearest")
        rotation = Rotation(rotation_angle,
                            Rotation.center_from_img(gray))

        if self.debug_level >= DebugLevel.MAIN:
            imshow(rotated, cmap="gray")
            self.savers_['result'].save(raw_data.name)

        return TransformedImageData(raw_data, rotated,
                                    rotation)

    def get_gray_(self, raw_data: RawData):
        img = rgb2gray(raw_data.img)

        if self.debug_level >= DebugLevel.ALL:
            imshow(img, cmap="gray")
            self.savers_['gray'].save(raw_data.name)

        return img

    def get_enhanced_image_(self, raw_data: RawData,
                            img: array) -> array:
        image = sobel(img)
        image = threshold(image, threshold_otsu(image))
        image = closing(image)

        if self.debug_level >= DebugLevel.ALL:
            imshow(image, cmap="gray")
            self.savers_['enhanced'].save(raw_data.name)

        return image

    def get_angles_(self, raw_data: RawData,
                    img: array) -> array:
        tested_angles = linspace(pi / 4, 3 * pi / 4, 360)
        h, theta, d = hough_line(img,
                                 theta=tested_angles)
        _, angles, dists = \
            hough_line_peaks(h, theta, d,
                             threshold=.8 * amax(h),
                             min_distance=2)

        if self.debug_level >= DebugLevel.ALL:
            imshow(raw_data.img)
            origin = array((0, img.shape[1] - 1))
            for angle, dist in zip(angles, dists):
                y0, y1 = (dist - origin * cos(angle)) / \
                         sin(angle)
                plot(origin, (y0, y1), 'r-')
            ylim((img.shape[0], 0))
            self.savers_['lines'].save(raw_data.name)

        return angles
