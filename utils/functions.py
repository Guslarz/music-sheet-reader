from numpy import array, percentile
from typing import Union


def threshold(img: array, value: Union[float, array]) -> array:
    return (img > value) * 1


def contrast(img: array, l_percentile: float, r_percentile: float):
    min_val = percentile(img, l_percentile)
    max_val = percentile(img, 100 - r_percentile)
    diff = max_val - min_val

    res = (img - min_val) / diff
    res[res > 1] = 1
    res[res < 0] = 0

    return res
