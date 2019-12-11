from typing import Dict, Optional

import numpy as np

from neuron_morphology.morphology import Morphology


class UprightTransform(object):
    """Handles transformations to a pia/wm aligned coordinate frame."""

    def __init__(self, affine):
        """Represent upright transform as an affine array internally.

        :param affine: 4x4 array describing an affine transformation
        :type affine: array-like
        """
        self.affine = np.asarray(affine)
        assert self.affine.shape == (4, 4)

    @classmethod
    def from_dict(cls, affine_dict: Dict[str, float]):
        """Create a UprightTransform from a dict with keys and values.

        [[tvr_00 tvr_01 tvr_02 tvr_09]
         [tvr_03 tvr_04 tvr_05 tvr_10]
         [tvr_06 tvr_07 tvr_08 tvr_11]
         [0      0      0      1]]
        """
        transform = np.reshape([affine_dict['tvr_%02d' % i] for i in range(9)],
                               (3, 3))
        translation = np.reshape([affine_dict['tvr_%02d' % i]
                                 for i in range(9, 12)], (3, 1))
        affine = affine_from_transform_translation(transform, translation)

        return cls(affine)

    def to_dict(self) -> Dict:
        """Create dictionary defining the transformation.

        [[tvr_00 tvr_01 tvr_02 tvr_09]
         [tvr_03 tvr_04 tvr_05 tvr_10]
         [tvr_06 tvr_07 tvr_08 tvr_11]
         [0      0      0      1]]
        """
        affine_dict = {}
        for i in range(9):
            affine_dict['tvr_%02d' % i] = self.affine[0:3, 0:3].flatten()[i]

        for i in range(3):
            affine_dict['tvr_%02d' % (i + 9)] = \
                self.affine[3, 0:3].flatten()[i]

        return affine_dict

    @classmethod
    def from_coords_str(cls,
                        soma_coords_str: str,
                        pia_coords_str: str,
                        wm_coords_str: str,
                        soma_res: Optional[str]=None,
                        pia_res: Optional[str]=None,
                        wm_res: Optional[str]=None):
        """."""
        soma_coords = convert_coords_str(soma_coords_str, soma_res)
        pia_coords = convert_coords_str(pia_coords_str, pia_res)
        wm_coords = convert_coords_str(wm_coords_str, wm_res)
        return cls.from_coords(soma_coords, pia_coords, wm_coords)

    @classmethod
    def from_coords(cls, soma_coords, pia_coords, wm_coords):
        """Calculate upright angle relative to pia and wm.

        :param soma_coords: dictionary containing x and y np.arrays
            drawing the soma
        :type soma_coords: dict
        :param pia_coords: dictionary containing x and y np.arrays
            drawing the pia boundary
        :type pia_coords: dict
        :param wm_coords: dictionary containing x and y np.arrays
            drawing the wm boundary
        :type wm_coords: dict
        """
        raise NotImplementedError

    def transform(self, vector):
        """Apply the transform to input vector.

        :param vector: 3D vector or (3xn) array of vectors to be transformed
        :type vector: array-like
        :rtype: :py:class:`numpy.ndarray` with same shape as input
        """
        vector = np.asarray(vector)
        dims = len(vector.shape)
        if dims == 1:
            vector = vector.reshape((3, 1))
        vector = np.vstack((vector, np.ones((1, vector.shape[1]))))

        vec_t = np.dot(self.affine, vector)[0:3, :]
        if dims == 1:
            vec_t = vec_t.reshape((3,))

        return vec_t

    def _get_scaling_factor(self) -> float:
        """Calculate the scaling factor from the affine matrix.

        The determinant is the change in volume that occurs during
        transformation. The scaling factor is the 3rd root of the
        determinant.
        """
        determinant = np.linalg.det(self.affine)
        return np.power(abs(determinant), 1.0 / 3.0)

    def transform_morphology(self, morphology: Morphology,
                             clone: bool=False) -> Morphology:
        """Apply an affine transform to all nodes in a morphology."""
        if clone:
            morphology = morphology.clone()

        scaling_factor = self._get_scaling_factor()

        for node in morphology.nodes():
            coordinates = np.array((node['x'], node['y'], node['z'], 1),
                                   dtype=float)
            new_coordinates = self.transform(coordinates)
            node['x'] = new_coordinates[0]
            node['y'] = new_coordinates[1]
            node['z'] = new_coordinates[2]
            # approximate with uniform scaling in each dimension
            node['radius'] *= scaling_factor

        return morphology


def convert_coords_str(coords_str: str, resolution: Optional[str] = None):
    """Convert a comma seperated string of coordinate pairs.

    :param coords_str: string of coordinate pairs "x1,y1,x2,y2..."
    :type coords_str: str
    :param resolution: str representation of pixel resolution
    :type resolution: str
    :rtype: dict of x and y values
    """
    vals = coords_str.split(',')

    if resolution:
        resolution = float(resolution)
    else:
        resolution = 1.0

    x = np.asarray(vals[0::2], dtype=float) * resolution
    y = np.asarray(vals[1::2], dtype=float) * resolution
    coords = {'x': x, 'y': y}

    return coords


def affine_from_transform_translation(transform=None,
                                      translation=None,
                                      translate_first=False):
    """Create affine from linear transformation and translation.

    Affine transformation of vector x -> Ax + b in 3D:
    [A,       b
     0, 0, 0, 1]
    A is a 3x3 linear tranformation
    b is a 3x1 translation

    :param transform: linear transformation (3, 3)
    :type transformation: array-like
    :param translation: linear translation (3, 1)
    :type translation: array-like
    :param translate_first: apply the translation first
    :type translate_first: bool
    :rtype: :py:class:`numpy.ndarray' (4, 4) affine matrix
    """
    if transform is None:
        transform = np.eye(3)
    else:
        transform = np.asarray(transform)

    if translation is None:
        translation = np.zeros((3, 1))
    else:
        translation = np.reshape(translation, (3, 1))
        if translate_first:
            translation = transform.dot(translation)

    affine = np.zeros((4, 4))
    affine[0:3, 0:3] = transform
    affine[0:3, [3]] = translation
    affine[3, 3] = 1.0

    return affine


def rotation_from_angle(angle, axis=2):
    """Create an affine matrix from a rotation about a specific axis.

    :param angle: rotation angle in radians
    :type angle: float (rad)
    :param axis: axis to rotate about, 0=x, 1=y, 2=z (default = 2)
    :type axis: int
    :rtype: :py:class:`numpy.ndarray' (4, 4) affine matrix
    """
    c = np.cos(angle)
    s = np.sin(angle)

    if axis == 0:
        rot = np.asarray([[1, 0, 0],
                          [0, c, -s],
                          [0, s, c]])
    elif axis == 1:
        rot = np.asarray([[c, 0, s],
                          [0, 1, 0],
                          [-s, 0, c]])
    elif axis == 2:
        rot = np.asarray([[c, -s, 0],
                          [s, c, 0],
                          [0, 0, 1]])
    else:
        raise ValueError('axis must be 0, 1, or 2')

    return rot


def affine_from_translation(translation):
    """Create an affine translation.

    :param translation: vector of x, y, and z translations
    :type translation: array-like
    :rtype: :py:class:`numpy.ndarray' (4, 4) affine matrix
    """
    return affine_from_transform_translation(translation=translation)


def affine_from_transform(transform):
    """Create affine transformation.

    :param transformation: 3 x 3 row major transformation
    :type transformation: array-like
    :rtype: :py:class:`numpy.ndarray' (4, 4) affine matrix
    """
    return affine_from_transform_translation(transform=transform)
