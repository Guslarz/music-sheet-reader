from __future__ import annotations

from base.processor import Processor
from utils.data import LineData, SelectedObjectData
from utils.bbox import BBox
from utils.transformation import Translation
from utils.debug_saver import DebugSaver
from config import DebugLevel

from skimage.measure import find_contours
from matplotlib.pyplot import imshow, plot, subplots


class ObjectsSelector(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savers_ = {
            'lines': DebugSaver('selected_on_lines'),
            'global': DebugSaver('selected_on_initial_image')
        }

    def get_objects_data(self, data: list[LineData]) -> list[SelectedObjectData]:
        result = [obj for objects_data in
                  map(self.process_single_line_, data)
                  for obj in objects_data]

        result.sort(key=lambda obj: (obj.line.height, obj.offset_x))
        for i, obj in enumerate(result):
            obj.order = i

        for line in data:
            line.objects.sort(key=lambda obj: obj.order)
            for i, obj in enumerate(line.objects):
                obj.line_order = i

        raw_data = data[0].raw_data

        if self.debug_level >= DebugLevel.MAIN:
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

        if self.debug_level >= DebugLevel.ALL:
            print(result)

        return [
            SelectedObjectData(
                data,
                bbox.crop_image(data.img),
                Translation(bbox.offset),
                Translation(bbox.offset, parent=data.transformation)
            ) for bbox in result
        ]
