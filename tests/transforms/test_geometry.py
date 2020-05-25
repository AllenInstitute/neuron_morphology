import sys
import unittest

from neuron_morphology.transforms import geometry as geo

class TestCCW(unittest.TestCase):

    def test_ccw_correct(self):
        """
            line1 (0, 1) <- (1, 1)
            line2 (0, 0) -> (1, 0)
        """
        line1 = [(1, 1), (0, 1)]
        line2 = [(0, 0), (1, 0)]
        result = geo.get_ccw_vertices_from_two_lines(line1, line2)
        self.assertEqual(result, [(1, 1), (0, 1), (0, 0), (1, 0), (1, 1)])

    def test_ccw_line2_cw(self):
        """
            line1 (0, 1) <- (1, 1)
            line2 (0, 0) <- (1, 0)
        """
        line1 = [(1, 1), (0, 1)]
        line2 = [(1, 0), (0, 0)]
        result = geo.get_ccw_vertices_from_two_lines(line1, line2)
        self.assertEqual(result, [(1, 1), (0, 1), (0, 0), (1, 0), (1, 1)])

    def test_ccw_line1_cw(self):
        """
            line1 (0, 1) -> (1, 1)
            line2 (0, 0) -> (1, 0)
        """
        line1 = [(0, 1), (1, 1)]
        line2 = [(0, 0), (1, 0)]
        result = geo.get_ccw_vertices_from_two_lines(line1, line2)
        self.assertEqual(result, [(0, 1), (0, 0), (1, 0), (1, 1), (0, 1)])

    def test_ccw_both_cw(self):
        """
            line1 (0, 1) -> (1, 1)
            line2 (0, 0) <- (1, 0)
        """
        line1 = [(0, 1), (1, 1)]
        line2 = [(1, 0), (0, 0)]
        result = geo.get_ccw_vertices_from_two_lines(line1, line2)
        self.assertEqual(result, [(0, 1), (0, 0), (1, 0), (1, 1), (0, 1)])

class TestSnipCornerLoops(unittest.TestCase):

    def test_snip_corner_loops(self):
        ring_coords_with_corner_loops = [
            (1,5), (3,6), (5,6), (4,7), (4,2), (5,3), (4,3), (2,2), (1,5)
        ]
        expected = [
            (1, 5), (3, 6), (4, 6), (4, 3), (2, 2), (1, 5)
        ]
        obtained = geo.snip_corner_loops(ring_coords_with_corner_loops)
        assert expected == obtained
