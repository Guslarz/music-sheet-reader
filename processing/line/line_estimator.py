from __future__ import annotations

from base.processor import Processor
from utils.estimated_values import CommonEstimatedValues, \
    LineEstimatedValues
from utils.data import TransformedImageData, LineData
from utils.debug_saver import DebugSaver
from config import DebugLevel

from skimage.transform import hough_line, hough_line_peaks
from operator import attrgetter
from collections import Counter
from matplotlib.pyplot import subplots
from numpy import array, linspace, pi, arange, cos, sin, round


class LineEstimator(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'lines-heights': DebugSaver('estim_lines_heights')
        }

    def get_lines_data(self, data: list[TransformedImageData]) -> list[LineData]:
        common = self.get_common_values_(data)
        lines_values = [*map(self.get_line_values_, data)]

        if self.debug_level >= DebugLevel.MAIN:
            _, axes = subplots(nrows=len(data))
            for ax, image_data, values in zip(axes, data, lines_values):
                ax.imshow(image_data.img, cmap="gray")
                for line in values.staff_lines:
                    ax.plot(line[:, 1], line[:, 0], 'r-')
            self.savers_['lines-heights'].save(image_data.name)

        return [
            LineData(image_data, common, line_values)
            for image_data, line_values in zip(data, lines_values)
        ]

    def get_common_values_(self, data: list[TransformedImageData]) -> CommonEstimatedValues:
        images = map(attrgetter('img'), data)

        all_white = []
        all_black = []

        def handle_column(column):
            white = []
            black = []
            count = 0
            curr_type = column[0]
            for j in range(len(column)):
                if column[j] == curr_type:
                    count += 1
                else:
                    if curr_type == 0:
                        black.append(count)
                    else:
                        white.append(count)
                    count = 1
                    curr_type = column[j]
            if curr_type == 0:
                black.append(count)
            else:
                white.append(count)

            return white, black

        def handle_image(image):
            for i in range(image.shape[1]):
                column = image[:, i]
                white, black = handle_column(column)
                all_white.extend(white)
                all_black.extend(black)

        for img in images:
            handle_image(img)

        white_counter = Counter(all_white)
        black_counter = Counter(all_black)

        # inverted colors
        line_spacing = black_counter.most_common(1)[0][0]
        line_width = white_counter.most_common(1)[0][0]

        if self.debug_level >= DebugLevel.ALL:
            print(line_width, line_spacing)

        return CommonEstimatedValues(line_width, line_spacing)

    def get_line_values_(self, data: TransformedImageData) -> LineEstimatedValues:
        image = data.img

        tested_angles = linspace(pi / 2 - pi / 45,
                                 pi / 2 + pi / 45, 60)
        h, theta, d = hough_line(image, theta=tested_angles)
        _, angles, dists = hough_line_peaks(h, theta, d,
                                            num_peaks=5,
                                            min_distance=2)

        x_vec = arange(0, image.shape[1])
        staff_lines = array([[
            (
                int(round((dist - x * cos(angle)) / sin(angle))),
                x
            ) for x in x_vec] for dist, angle in zip(dists, angles)
        ])

        if self.debug_level >= DebugLevel.ALL:
            print(staff_lines)

        return LineEstimatedValues(staff_lines)
