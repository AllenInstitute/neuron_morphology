import unittest
import os
import allensdk.neuron_morphology.swc_io as swc


class TestSWCIO(unittest.TestCase):

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    swc_file = os.path.join(data_dir, 'test_swc.swc')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSWCIO)
    unittest.TextTestRunner(verbosity=5).run(suite)
