import warnings

import numpy as np
from numpy import ndarray


def get_row_scales(array: ndarray) -> ndarray:
    """
    array: ndarray - a 2D array where each row is to have its scale calculated

    returns a 1D array that represents the scale of each row
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", "divide by zero encountered in log10"
        )
        warnings.filterwarnings(
            "ignore", "divide by zero encountered in reciprocal"
        )
        A_maxima = np.max(np.absolute(array), axis=1)
        scales = np.nan_to_num(
            np.power(
                10,
                np.floor(
                    np.log10(np.array(np.absolute(A_maxima), dtype=float))
                ),
            )
        )
        inv_scales = np.reciprocal(scales)
    return np.nan_to_num(inv_scales)


def get_order_ranges(array: ndarray) -> ndarray:
    """
    array: ndarray - a 2D array where each row is to have its order of magnitude range
    ( log10 (maximum/minimum) ) calculated. 0s are ignored.

    returns a 1D array that represents the order of magnitude range of each row
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", "divide by zero encountered in log10"
        )
        mags = np.log10(np.array(np.absolute(array), dtype=float))
    order_ranges = []
    for res in mags:
        new_res_list = []
        for i in res:
            if i != -np.inf:
                new_res_list.append(i)
        if len(new_res_list) > 0:
            order_range = np.ptp(new_res_list)
        else:
            order_range = 0
        order_ranges.append(order_range)
    return np.array(order_ranges)
