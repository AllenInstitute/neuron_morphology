import unittest
from tests.data import test_density_graph, test_morphology_large


class TestDensityGraph(unittest.TestCase):

    def test_max(self):

        density_graph = test_density_graph(width=30, height=100)
        expected_max = 435.0880552181651
        self.assertEqual(expected_max, density_graph.max())

    def test_top_small(self):

        density_graph = test_density_graph(width=30, height=100)
        expected_top = 9
        self.assertEqual(expected_top, density_graph.top())

    def test_top_large(self):

        morphology = test_morphology_large()
        density_graph = test_density_graph(morphology=morphology, width=30, height=100)
        expected_top = 9
        self.assertEqual(expected_top, density_graph.top())

    def test_bottom_small(self):

        density_graph = test_density_graph(width=30, height=100)
        expected_bottom = 19
        self.assertEqual(expected_bottom, density_graph.bottom())

    def test_bottom_large(self):

        morphology = test_morphology_large()
        density_graph = test_density_graph(morphology=morphology, width=30, height=100)
        expected_bottom = 23
        self.assertEqual(expected_bottom, density_graph.bottom())


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDensityGraph)
    unittest.TextTestRunner(verbosity=5).run(suite)
