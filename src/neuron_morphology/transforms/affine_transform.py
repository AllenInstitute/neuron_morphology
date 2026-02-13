from typing import List, Dict, Optional, Any

import numpy as np

from neuron_morphology.morphology import Morphology
from neuron_morphology.transforms.transform_base import TransformBase


class AffineTransform(TransformBase):
    """Handles transformations to a pia/wm aligned coordinate frame."""

    def __init__(self, affine: Optional[Any] = None):
        """
            Represent the transform as a (4,4) np.ndarray affine matrix

            Parameters
            ----------
            affine: (4,4) array-like affine transformation

        """
        if affine is None:
            self.affine = np.eye(4)
        else:
            self.affine = np.asarray(affine)
            assert self.affine.shape == (4, 4)

    @classmethod
    def from_dict(cls, affine_dict: Dict[str, float]):
        """
            Create an AffineTransform from a dict with keys and values.

            Parameters
            ----------
            affine_dict: keys and values corresponding to the following
                [[tvr_00 tvr_01 tvr_02 tvr_09]
                 [tvr_03 tvr_04 tvr_05 tvr_10]
                 [tvr_06 tvr_07 tvr_08 tvr_11]
                 [0      0      0      1]]

            Returns
            -------
            AffineTransform object

        """
        transform = np.reshape([affine_dict['tvr_%02d' % i] for i in range(9)],
                               (3, 3))
        translation = np.reshape([affine_dict['tvr_%02d' % i]
                                 for i in range(9, 12)], (3, 1))
        affine = affine_from_transform_translation(transform, translation)

        return cls(affine)

    @classmethod
    def from_list(cls, affine_list: List[float]):
        """
            Create an Affine Transform from a list

            Parameters
            ----------
            affine_list: list of tvr values corresponding to:
                [[tvr_00 tvr_01 tvr_02 tvr_09]
                 [tvr_03 tvr_04 tvr_05 tvr_10]
                 [tvr_06 tvr_07 tvr_08 tvr_11]
                 [0      0      0      1]]

            Returns
            -------
            AffineTransform object

        """
        transform = np.reshape(affine_list[0:9], (3, 3))
        translation = np.reshape(affine_list[9:12], (3, 1))
        affine = affine_from_transform_translation(transform, translation)

        return cls(affine)

    def to_dict(self) -> Dict:
        """
            Create dictionary defining the transformation.

            Returns
            -------
            Dict with keys and values corresponding to the following:

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
                self.affine[0:3, 3].flatten()[i]

        return affine_dict

    def to_list(self) -> List:
        """
            Create a list defining the transformation.

            Returns
            -------
            List with values corresponding to the following:

                [[tvr_00 tvr_01 tvr_02 tvr_09]
                 [tvr_03 tvr_04 tvr_05 tvr_10]
                 [tvr_06 tvr_07 tvr_08 tvr_11]
                 [0      0      0      1]]

        """
        affine_list = self.affine[0:3, 0:3].flatten().tolist()
        affine_list += self.affine[0:3, 3].flatten().tolist()

        return affine_list

    def transform(self, vector: Any) -> np.ndarray:
        """
            Apply this transform to (3,) point or (n,3) array-like of points.

            Parameters
            ----------
            vector: a (3,) array-like point or a (n,3) array-like array
                    of points to be transformed

            Returns
            -------
            numpy.ndarray with same shape as input

        """
        vector = np.asarray(vector)
        dims = len(vector.shape)
        if dims == 1:
            vector = vector.reshape((3, 1))
        else:
            vector = vector.T

        vector = np.vstack((vector, np.ones((1, vector.shape[1]))))

        vec_t = np.dot(self.affine, vector)[0:3, :]
        if dims == 1:
            vec_t = vec_t.reshape((3,))
        else:
            vec_t = vec_t.T

        return vec_t

    def _get_scaling_factor(self) -> float:
        """
            Calculate the scaling factor from the affine matrix.

            Returns
            -------
            Scaling factor: 3rd root of the determinant.

        """
        determinant = np.linalg.det(self.affine)
        return np.power(abs(determinant), 1.0 / 3.0)

    def transform_morphology(self,
                             morphology: Morphology,
                             clone: bool = False,
                             scale_radius: bool = True,
                             ) -> Morphology:
        """
            Apply this transform to all nodes in a morphology.

            Parameters
            ----------
            morphology: a Morphology loaded from an swc file
            clone: make a new object if True
            scale_radius: apply radius scaling if True

            Returns
            -------
            A Morphology
        """
        if clone:
            morphology = morphology.clone()

        if scale_radius:
            scaling_factor = self._get_scaling_factor()
        else:
            scaling_factor = 1

        for node in morphology.nodes():
            coordinates = np.array((node['x'], node['y'], node['z']),
                                   dtype=float)
            new_coordinates = self.transform(coordinates)
            node['x'] = new_coordinates[0]
            node['y'] = new_coordinates[1]
            node['z'] = new_coordinates[2]
            # approximate with uniform scaling in each dimension
            node['radius'] *= scaling_factor

        return morphology


def affine_from_transform_translation(transform: Optional[Any] = None,
                                      translation: Optional[Any] = None,
                                      translate_first: bool = False):
    """
        Create affine from linear transformation and translation.

        Affine transformation of vector x -> Ax + b in 3D:
        [A,       b
         0, 0, 0, 1]
        A is a 3x3 linear tranformation
        b is a 3x1 translation

        Parameters
        ----------
        transform: linear transformation (3, 3) array-like
        translation: linear translation (3,) array-like
        translate_first: apply the translation before the transform

        Returns
        -------
        (4, 4) numpy.ndarray affine matrix

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


def rotation_from_angle(angle: float, axis: int = 2):
    """
        Create an affine matrix from a rotation about a specific axis.

        Parameters
        ----------
        angle: rotation angle in radians
        axis: axis to rotate about, 0=x, 1=y, 2=z (default z axis)

        Returns
        -------
        (3, 3) numpy.ndarray rotation matrix

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


def affine_from_translation(translation: Any):
    """
        Create an affine translation.

        Parameters
        ----------
        translation: array-like vector of x, y, and z translations

        Returns
        -------
        (4, 4) numpy.ndarray affine matrix

    """
    return affine_from_transform_translation(translation=translation)


def affine_from_transform(transform: Any):
    """Create affine transformation.

        Parameters
        ----------
        transformation: (3, 3) row major array-like transformation

        Returns
        -------
        (4, 4) numpy.ndarray affine matrix

    """
    return affine_from_transform_translation(transform=transform)
