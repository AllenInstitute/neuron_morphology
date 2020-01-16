from typing import Dict, Optional

import numpy as np

from scipy.spatial import Voronoi
from scipy.spatial.distance import euclidean
from shapely.geometry import LineString, MultiPoint

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
                        wm_res: Optional[str]=None,
                        n_interp: Optional[int]=0):
        """Convert strings to coords and calls from_coords()."""
        soma_coords = convert_coords_str(soma_coords_str, soma_res)
        pia_coords = convert_coords_str(pia_coords_str, pia_res)
        wm_coords = convert_coords_str(wm_coords_str, wm_res)
        return cls.from_coords(soma_coords, pia_coords, wm_coords, n_interp)

    @classmethod
    def from_coords(cls, soma_coords, pia_coords, wm_coords,
                    n_interp: Optional[int]=0):
        """Calculate upright angle relative to pia and wm.

        Uses Voronoi diagram to fit an intermediate path between
        the pia and wm, and constructs a line perpendicular to it
        through the soma

        :param soma_coords: dictionary containing x and y np.arrays
            drawing the soma
        :type soma_coords: dict
        :param pia_coords: dictionary containing x and y np.arrays
            drawing the pia boundary
        :type pia_coords: dict
        :param wm_coords: dictionary containing x and y np.arrays
            drawing the wm boundary
        :type wm_coords: dict
        :param n_interp: number of points to interpolate per line
        :type n_interp: int
        """
        # Approximate soma centroid as average of coords
        soma = np.asarray((soma_coords['x'].mean(), soma_coords['y'].mean()))
        x = []
        y = []
        for coords in [pia_coords, wm_coords]:
            # Interpolate coordinates
            if n_interp > 0:
                for i in range(coords['x'].shape[0] - 1):
                    x += np.linspace(coords['x'][i],
                                     coords['x'][i + 1],
                                     2 + n_interp).tolist()
                    y += np.linspace(coords['y'][i],
                                     coords['y'][i + 1],
                                     2 + n_interp).tolist()
            else:
                x += coords['x'].tolist()
                y += coords['y'].tolist()

        all_points = np.asarray((x, y)).T

        # Construct voronoi
        v_diagram = Voronoi(all_points)
        vertices = v_diagram.vertices
        ridge_vertices = v_diagram.ridge_vertices

        hull = MultiPoint(all_points).convex_hull

        # Get ridges in between points
        mid_line = []  # list of mid line segments

        for vertex_indices in ridge_vertices:
            vertex_indices = np.asarray(vertex_indices)
            # vertex -1 indicates infinite line, don't include
            if np.all(vertex_indices >= 0):
                segment = [(x, y) for x, y in vertices[vertex_indices]]
                # only include segments between the pia and wm
                if LineString(segment).within(hull):
                    mid_line.append(segment)

        # Remove perpendicular lines from centerline
        angles = [np.arctan((seg[1][1] - seg[0][1]) / (seg[1][0] - seg[0][0]))
                  for seg in mid_line]
        median_angle = np.median(angles)
        threshold = np.radians(30)
        j = 0
        for angle in angles:
            # angles are between -pi/2 and pi/2
            if (abs(angle - median_angle) < threshold or
                    0 < abs(angle - median_angle) - np.pi < threshold):
                j += 1
            else:
                mid_line.pop(j)

        # Find minimum projection to ridge
        min_dist = None
        min_proj = None
        for segment in mid_line:
            dist, proj = dist_proj_point_lineseg(soma,
                                                 np.asarray(segment[0]),
                                                 np.asarray(segment[1]),
                                                 clamp_to_segment=True)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                min_proj = proj

        # angle from +x axis
        theta = np.arctan2((min_proj[1] - soma[1]), (min_proj[0] - soma[0]))

        # if the soma is between the midline and the pia, rotate angle by 180
        u_x = (min_proj[0] - soma[0]) / min_dist
        u_y = (min_proj[1] - soma[1]) / min_dist
        extent = euclidean((max(x), max(y)), (min(x), min(y)))
        arrow = LineString([soma, soma + np.asarray([u_x, u_y]) * extent])
        pia_linestring = LineString(np.asarray([pia_coords['x'],
                                                pia_coords['y']]).T)
        wm_linestring = LineString(np.asarray([wm_coords['x'],
                                               wm_coords['y']]).T)

        crosses_pia = arrow.crosses(pia_linestring)
        crosses_wm = arrow.crosses(wm_linestring)
        if crosses_pia and not crosses_wm:
            # The projection is in the same direction as the pia
            pass
        elif crosses_wm and not crosses_pia:
            # The project is in the opposite direction of the pia
            theta = theta - np.pi
        else:
            raise Exception('Vertical projection crosses both '
                            'wm and pia or neither')

        # get angle from +y axis ()
        theta = np.pi / 2 - theta
        rot = rotation_from_angle(theta, axis=2)

        # get soma x,y,z translation (z translation set to 0)
        translation = np.append(-soma, 0)

        # translate, then rotate
        affine = affine_from_transform_translation(translation=translation,
                                                   transform=rot,
                                                   translate_first=True)

        return cls(affine), v_diagram, mid_line, min_proj, theta

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
            coordinates = np.array((node['x'], node['y'], node['z']),
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


def project_to_polyline(coords, target_point):
    x, y = coords["x"], coords["y"]
    points = list(map(np.array, zip(x, y)))
    dists_projs = [dist_proj_point_lineseg(target_point, q1, q2)
                   for q1, q2 in zip(points[:-1], points[1:])]
    min_idx = np.argmin(np.array([d[0] for d in dists_projs]))

    # check if the closes point is the endpoint of the whole polyline
    # - if so, extend past the edge
    if np.allclose(dists_projs[min_idx][0], points[0]) or np.allclose(dists_projs[min_idx][0], points[-1]):
        return dist_proj_point_lineseg(target_point, points[min_idx],
                                       points[min_idx + 1], clamp_to_segment=False)[1]
    else:
        return dists_projs[min_idx][1]


def dist_proj_point_lineseg(p, q1, q2, clamp_to_segment=True):
    """Find the projection of a point onto a line segment and its distance.

    based on c code from
    http://stackoverflow.com/questions/849211/shortest-distance-between-
    a-point-and-a-line-segment

    :param p: point to project
    :type p: array-like
    :param q1: end point of line segment
    :type q1: array-like
    :param q2: other endpoint of line segment
    :type q2: array-like
    :param clamp_to_segment: require projection to be on linesegement
    :type: bool
    """
    l2 = euclidean(q1, q2) ** 2
    if l2 == 0:
        return euclidean(p, q1), q1  # q1 == q2 case
    if clamp_to_segment:
        t = max(0, min(1, np.dot(p - q1, q2 - q1) / l2))
    else:
        t = np.dot(p - q1, q2 - q1) / l2
    proj = q1 + t * (q2 - q1)
    return euclidean(p, proj), proj


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
