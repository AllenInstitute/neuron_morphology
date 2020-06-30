import unittest
import sys

from shapely.geometry import LineString, Point

import neuron_morphology.snap_polygons.cortex_surfaces as cs


class TestStandalone(unittest.TestCase):
    """Tests for functions operating on shapely objects
    """

    def test_remove_duplicates(self):
        cases = [
            [
                [Point(0, 1), Point(0, 1), Point(1, 1), Point(0, 1)],
                [Point(0, 1), Point(1, 1), Point(0, 1)]
            ],
            [
                [Point(0, 1), Point(0, 0), Point(0, 0), Point(0, 0)],
                [Point(0, 1), Point(0, 0)]
            ],
            [
                [Point(0, 1), Point(0.0, 1.0), Point(1, 1)],
                [Point(0, 1), Point(1, 1)]
            ],
            [
                [Point(0, 1), Point(sys.float_info.epsilon, 1), Point(1, 1)],
                [Point(0, 1), Point(sys.float_info.epsilon, 1), Point(1, 1)]
            ]
        ]

        for inpt, expected in cases:
            with self.subTest():
                obtained = cs.remove_duplicates(inpt)
                self.assertEqual(LineString(obtained), LineString(expected))

    def test_find_transition(self):
        condition = lambda pt: Point(0, 0).distance(pt) <= 1
        cases = [
            [Point(0, -2), Point(0, 0), 0, Point(0, -1)],
            [Point(0, -3), Point(0, 0), 0, Point(0, 0)],
            [Point(0, -4), Point(0, 0), 2, Point(0, -1)],
            [Point(0, -4), Point(0, -1), 10, Point(0, -1)],
            [Point(0, -1.5), Point(0, 0.5), 1, Point(0, -1)]
        ]

        for unmet, met, iterations, expected in cases:
            with self.subTest():
                obtained = cs.find_transition(
                    unmet, met, condition, iterations)
                print(obtained.xy, expected.xy)
                self.assertEqual(obtained, expected)


class TestCompound(unittest.TestCase):
    """Tests for functions operating on other cortex_surfaces functions
    """

    def test_first_met(self):
        condition = lambda pt: Point(0, 0).distance(pt) <= 1
        cases = [
            [
                [(-4, 0), (-3, 0), (-2, 0), (-1, 0), (0, 0)],
                2,
                3,
                Point(-1, 0)
            ],
            [
                [Point(0, 0), Point(1, 0), Point(2, 0)],
                30,
                0,
                Point(0, 0)
            ]
        ]

        for coords, iterations, idx_exp, coord_exp in cases:
            with self.subTest():
                idx_obt, coord_obt = cs.first_met(
                    coords, condition, iterations)
                print(idx_obt, idx_exp, coord_obt, coord_exp)
                self.assertEqual(idx_obt, idx_exp)
                self.assertEqual(coord_obt, coord_exp)

    def test_trim_coords(self):
        condition = lambda pt: Point(0, 0).distance(pt) <= 1
        cases = [
            [
                [Point(-2, 0), Point(-1, 0), Point(0, 0), Point(1, 0), Point(2, 0)],
                10,
                [Point(-1, 0), Point(0, 0), Point(1, 0)]
            ],
            [
                [Point(-2.5, 0), Point(-1.5, 0), Point(0.5, 0), Point(1.5, 0), Point(2.5, 0)],
                10,
                [Point(-1.0, 0), Point(0.5, 0), Point(1.0, 0)]
            ]
        ]

        for coords, iterations, expected in cases:
            with self.subTest():
                obtained = cs.trim_coords(coords, condition, iterations)
                ls_obt = LineString(obtained)
                ls_exp = LineString(expected)
                print(ls_obt, ls_exp)
                self.assertEqual(ls_obt, ls_exp)

    def trim_to_close(self):
        cases = [
            [
                [Point(-2, 0), Point(-1, 0), Point(0, 0), Point(1, 0), Point(2, 0)],
                1.0,
                10,
                [Point(-1, 0), Point(0, 0), Point(1, 0)]
            ],
            [
                [Point(-2.5, 0), Point(-1.5, 0), Point(0.5, 0), Point(1.5, 0), Point(2.5, 0)],
                1.0,
                10,
                [Point(-1.0, 0), Point(0.5, 0), Point(1.0, 0)]
            ],
            [
                [Point(-2.5, 0), Point(-1.5, 0), Point(0.5, 0), Point(1.5, 0), Point(2.5, 0)],
                2.0,
                10,
                [Point(-2.0, 0), Point(-1.5, 0), Point(0.5, 0), Point(1.5, 0), Point(2.0, 0)]
            ]
        ]

        for coords, threshold, iterations, expected in cases:
            with self.subTest():
                obtained = cs.trim_to_close(Point(0, 0), threshold, LineString(coords), iterations)
                ls_obt = LineString(obtained)
                ls_exp = LineString(expected)
                print(ls_obt, ls_exp)
                self.assertEqual(ls_obt, ls_exp)