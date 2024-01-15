"""
Implementation based on equations in Appendix A of https://ojs.aaai.org/index.php/HCOMP/article/view/13306/13154

By no means is this compute efficient, but it is easy to understand and implement.
"""

from collections import Counter
from math import factorial
from typing import Callable


def nPr(n, r):
    return int(factorial(n) / factorial(n - r))


def calc_disagreement(
    values: list[tuple[int]], distance_metric: Callable[[tuple[int], tuple[int]], float]
):
    value_count = Counter(values)
    return sum(
        distance_metric(value_1, value_2) * count_1 * count_2 / nPr(len(values), 2)
        for value_1, count_1 in value_count.items()
        for value_2, count_2 in value_count.items()
    )


def calc_observed_disagreement(
    multi_annotated_fields: list[list[tuple[int]]],
    distance_metric: Callable[[tuple[int], tuple[int]], float],
):
    total_num_annotations = sum(
        len(multi_annotated_field) for multi_annotated_field in multi_annotated_fields
    )
    return sum(
        (len(multi_annotated_field) / total_num_annotations)
        * calc_disagreement(multi_annotated_field, distance_metric)
        for multi_annotated_field in multi_annotated_fields
    )


def calc_expected_disagreement(
    multi_annotated_fields: list[list[tuple[int]]],
    distance_metric: Callable[[tuple[int], tuple[int]], float],
):
    return calc_disagreement(
        [
            field_annotation
            for multi_annotated_field in multi_annotated_fields
            for field_annotation in multi_annotated_field
        ],
        distance_metric,
    )


def calc_krippendorffs_alpha(multi_annotated_fields, delta_distance):
    observed_disagreement = calc_observed_disagreement(
        multi_annotated_fields, delta_distance
    )
    expected_disagreement = calc_expected_disagreement(
        multi_annotated_fields, delta_distance
    )
    return 1 - observed_disagreement / expected_disagreement
