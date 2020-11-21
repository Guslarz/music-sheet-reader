from __future__ import annotations

from base.processor import Processor
from utils.data import LineData, SelectedObjectData
from utils.bbox import BBox
from utils.transformation import Translation
from utils.debug_saver import DebugSaver
from config import DebugLevel

from skimage.measure import find_contours
from skimage.transform import hough_line, hough_line_peaks
from matplotlib.pyplot import imshow, plot, subplots
from numpy import linspace, pi


class ObjectsSelector(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'vertical': DebugSaver('selector_vertical_lines'),
            'lines': DebugSaver('selected_on_lines'),
            'global': DebugSaver('selected_on_initial_image')
        }

    def get_objects_data(self, data: list[LineData]) -> list[SelectedObjectData]:
        result = [obj for objects_data in
                  map(self.process_single_line_, data)
                  for obj in objects_data]

        result.sort(key=lambda obj: (obj.line.height, obj.line_order))
        for i, obj in enumerate(result):
            obj.order = i

        raw_data = data[0].raw_data

        if self.debug_level >= DebugLevel.REPORT:
            _, axes = subplots(nrows=len(data))
            for ax, line in zip(axes, data):
                ax.imshow(line.img, cmap="gray")
                for obj in line.objects:
                    points = BBox.from_image(obj.img).to_points()
                    points = obj.line_transformation.apply_to_points(points)
                    ax.plot(points[:, 1], points[:, 0])
            self.savers_['lines'].save(raw_data.name)

        if self.debug_level >= DebugLevel.MAIN:
            imshow(raw_data.img)
            for obj in result:
                points = BBox.from_image(obj.img).to_points()
                points = obj.global_transformation.apply_to_points(points)
                plot(points[:, 1], points[:, 0])
            self.savers_['global'].save(raw_data.name)

        return result

    def process_single_line_(self, data: LineData) -> list[SelectedObjectData]:
        margin = 0
        contours = find_contours(data.img, .5)
        bounding_boxes = map(BBox.from_contour, contours)
        result = []

        def find_connected(bbox):
            for i, other in enumerate(result):
                if bbox.min_x - margin <= other.min_x <= bbox.max_x + margin:
                    return i
                if bbox.min_x - margin <= other.max_x <= bbox.max_x + margin:
                    return i
                if other.min_x - margin <= bbox.min_x <= other.max_x + margin:
                    return i
                if other.min_x - margin <= bbox.max_x <= other.max_x + margin:
                    return i
            return None

        for curr in bounding_boxes:
            index = find_connected(curr)
            while index is not None:
                connected = result[index]
                result.pop(index)
                curr = BBox.merge(curr, connected)
                index = find_connected(curr)
            result.append(curr)

        result = [*filter(lambda bbox: bbox.max_x - bbox.min_x >= data.line_spacing, result)]

        result.sort(key=lambda res: res.min_x)
        first, *rest = result

        if self.debug_level >= DebugLevel.ALL:
            imshow(data.img, cmap="gray")
        rest = [res
                for bbox in rest
                for res in self.separate_connected(data, bbox)]
        if self.debug_level >= DebugLevel.ALL:
            self.savers_['vertical'].save(data.name)

        result = [first, *rest]
        result = [*filter(lambda bbox: bbox.max_x - bbox.min_x >= data.line_spacing, result)]

        return [
            SelectedObjectData(
                data,
                bbox.crop_image(data.img),
                Translation(bbox.offset),
                Translation(bbox.offset, parent=data.transformation)
            ) for bbox in result
        ]

    def separate_connected(self, data: LineData, bbox: BBox) -> list[BBox]:
        tmp = BBox(bbox.min_x, 0, bbox.max_x, data.img.shape[0] - 1)
        img = tmp.crop_image(data.img).T

        tested_angles = linspace(pi / 2 - pi / 45,
                                 pi / 2 + pi / 45, 10)
        h, theta, d = hough_line(img, theta=tested_angles)
        _, angles, dists = hough_line_peaks(h, theta, d,
                                            min_distance=data.line_spacing // 2,
                                            threshold=data.line_spacing * 3)
        dists.sort()

        if self.debug_level >= DebugLevel.ALL:
            for dist in dists:
                plot((bbox.min_x + dist, bbox.min_x + dist),
                     (0, data.img.shape[0] - 1),
                     'r-')

        if len(dists) <= 1:
            return [bbox]

        split_lines = [
            0,
            *[(dists[i] + dists[i + 1]) / 2
              for i in range(len(dists) - 1)],
            bbox.max_x - bbox.min_x + 1
        ]

        bounding_boxes = []
        for i in range(len(split_lines) - 1):
            tmp = BBox(
                bbox.min_x + split_lines[i],
                bbox.min_y,
                bbox.min_x + split_lines[i + 1] - 1,
                bbox.max_y
            )
            bounding_boxes.append(tmp)

        bounding_boxes = [*filter(lambda x: (x.crop_image(data.img)[:, :] != 0).any(),
                                  bounding_boxes)]

        for bounding_box in bounding_boxes:
            img = bounding_box.crop_image(data.img)
            i = 0
            while (img[i, :] == 0).all():
                i += 1
            bounding_box.min_y += i

            i = -1
            while (img[i, :] == 0).all():
                i -= 1
            bounding_box.max_y += i

            i = 0
            while (img[:, i] == 0).all():
                i += 1
            bounding_box.min_x += i

            i = -1
            while (img[:, i] == 0).all():
                i -= 1
            bounding_box.max_x += i

        return bounding_boxes
