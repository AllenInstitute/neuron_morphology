import sys
import unittest

import numpy as np

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

    def test_prune_two_lines(self):
        """
            line1 (1, 1), (0, 1), (0.5, 1.5) -> (1, 1), (0, 1)
        """
        line1 = [(1, 1), (0, 1), (0.5, 1.5)]
        line2 = [(0, 0), (1, 0)]
        line1_pruned, line2_pruned = geo.prune_two_lines(line1, line2)
        self.assertEqual(line1_pruned, [(1, 1), (0, 1)])
