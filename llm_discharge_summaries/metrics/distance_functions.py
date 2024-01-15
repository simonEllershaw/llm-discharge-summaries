import numpy as np


def is_error(x: tuple[int], y: tuple[int]) -> float:
    if any(x_i != 0 for x_i in x) and any(y_i != 0 for y_i in y):
        return 0
    elif all(x_i == 0 for x_i in x) and all(y_i == 0 for y_i in y):
        return 0
    else:
        return 1


def delta_distance(x: tuple[int], y: tuple[int]) -> float:
    return 0 if x == y else 1


def l1_distance(x: tuple[int], y: tuple[int]) -> float:
    return sum(abs(x_i - y_i) for x_i, y_i in zip(x, y))


def rmse_distance(x: tuple[int], y: tuple[int]) -> float:
    return np.sqrt(np.mean(np.square(np.array(x) - np.array(y))))
