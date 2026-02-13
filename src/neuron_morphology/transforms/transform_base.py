import abc

from neuron_morphology.morphology import Morphology


class TransformBase(abc.ABC):
    """
        Abstract base class for implementing swc transforms.
        Each child class should implement these methods.
    """
    @abc.abstractmethod
    def transform_morphology(self) -> Morphology:
        """
            Apply this transform to all nodes in a morphology.

            Returns
            -------
            A Morphology

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def transform(self):
        """
            Apply this transform to (3,) point or (3,n) array-like of points.

            Returns
            -------
            numpy.ndarray with same shape as input

        """
        raise NotImplementedError()
