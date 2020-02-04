Snap Polygons
=============

Problem
-------

In order to calculate layered point depths, which are required for the layer histogram features, we need to be able to assign each node in a cortical morphological reconstruction to a layer. This is tricky, because the layer annotations are drawn as separate closed polygons, leaving layerless empty space in between.

Existing code does this task implicitly on a node-by-node basis. We would like to instead carry out a set of polygon adjustments once per slice and produce a visible artifact that can be independently investigated. This separation of concerns will make our pipeline more maintainable and easier to adjust for new data.


Approach
--------

1. produce a definitive raster mask from each polygon. This will require:
    1. calculating the bounding box of the set of polygons. This will determine the aspect ratio of our canvas
    1. separately rasterizing each polygon.
    1. deleting in each rasterization any pixels shared among polygons
1. Calculate the medial axis transform of each mask's negative space. This will result in a num_polys X height X width stack of distance images, whose values (through the stack) are the distances from a given pixel to each polygon.
1. Take an argmin through the stack of distance images. This will produce a label image whose values are the closest polygon at each pixel
1. clip this label image based a mask of all the polygons. These could be acquired by e.g. iterative binary closure.
1. vectorize each polygon
1. locate the pia-side surface of each polygon
    1. this could get a bit hairy. Probably the easiest way is to use the depth field. I don't have a non-heuristic approach at this point.
    1. another set of options could be to project the pia surface drawing onto the layer polygon. I don't have a good idea of what tools exist for doing this, but it bears investigation.
1. extract the pia-side surface from each polygon. These are the outputs of this module.


Tradeoffs
---------


Initial Design
--------------

#### inputs
1. a set of layer polygons. Each has:
    - a string label
    - a path, given as one of:
        - "x,y,x,y,..."
        - [[x, y], [x, y]]
1. a pair of pia, wm polylines. These are given as:
    - a string label
    - a path, as in the layer polygons
1. The width and height of the original image
1. Depths, as a path to a netcdf. Only if we end up using these for pia-side identification.
1. output paths
1. optionally, a set of images used as the basis for optional overlay outputs. These have:
    - the image path
    - an output path
    - optionally, an affine transform from the original image space to the space of the provided image

#### outputs
1. a set of snapped layer polygons. Each has:
    - a string name
    - a path, given as [[x, y], [x, y]]
    - a pia-side path, given as [[x, y], [x, y]]. This must be a subpath of the above
1. for each input image, an output image (path in the json) displaying the input image and the overlaid polygons / surfaces.

#### internals

At core, we will depend on a class like:
```Python
from shapely.geometry.polygon import Polygon, LinearRing
from shapely.geometry import LineString

PolyType = Union[
    str, 
    Sequence[Sequence[float]],
    Polygon, 
    LinearRing
]

LineType = Union[
    str,
    Sequence[Sequence[float]],
    LineString
]

TransformType = Callable[
    [float, float],
    [float, float]
]

class BoundingBox(NamedTuple):
    """
    """

    # one might think these should be int, but we want to be able to record precisely the actual bounding box of some polygons with float vertices (then scale and convert to int at a requested resolution when necessary)

    # near corner
    vert_origin: float 
    hor_origin: float

    # far corner
    vert_extent: float
    hor_extent: float

    @property
    def width(self) -> float:
        return self.hor_extent - self.hor_origin

    @property
    def height(self) -> float:
        return self.vert_extent - self.vert_origin

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height 

    def update(
        self, 
        vert_origin: float, 
        hor_origin: float, 
        vert_extent: float, 
        hor_extent: float
    ):
        """ Potentially enlarges this box.
        """

    def transform(self, transform: TransformType) -> BoundingBox:
        """ Apply a transform (not in place!) to this box.
        """

def ensure_polygon(candidate: PolyType) -> Polygon:
    """ Convert from one of many polygon representations to Polygon
    """

def ensure_linestring(candidate: LineType) -> LineString:
    """ Convert from one of many line representations to LineString
    """

class Geometries:

    def __init__(
        self, 
        original_space: BoundingBox
    ):
        """ A collection of polygons and lines
        """

        self.original_bounds: BoundingBox = original_space
        self.close_bounds: Optional[BoundingBox] = None

        self.polygons: Dict[str, Polygon] = {}
        self.lines: Dict[str, LineString] = {}

    def register_polygon(
        self, 
        name: str, 
        path: PolyType
    ):
        """ Adds a layer polygon path to this object. Updates the close bounding box.
        """

    def register_polygons(self, polygons: Dict[str, Polytype]):
        """ utility for registering multiple polygons
        """

    def register_surface(
        self, 
        name: str, 
        path: LineType
    ):
        """ Adds a line (e.g. the pia/wm surfaces) to this object. Updates the bounding box.
        """

    def register_surfaces(self, surfaces: Dict[str, Linetype]):
        """ utility for registering multiple surfaces
        """

    def rasterize(
        self, 
        shape: Optional[Tuple[int]] = None,
        polygons: Union[Sequence[str], bool] = True, 
        lines: Union[Sequence[str], bool] = False
    ) -> Dict[str, np.ndarray]:
        """ Rasterize one or more owned geometries. Produce a mapping from object names to masks.

        Parameters
        ----------
        shape : if provided, the output image shape. Otherwise, use     the rounded close bounding box shape
        polygons : a list of names. Alternatively all (True) or none    (False)
        lines : a list of names. Alternatively all (True) or none       (False)

        """

    def transform(
        self, 
        transform: TransformType
    ) -> "Geometries":
        """ Apply a transform to each owned geometry. Return a new collection.
        """

def make_scale_transform(scale: float) -> TransformType:
    """ Make a simple scale transformer
    """


def main(
    layer_polygons: Dict[str, PolyType],
    surfaces: Dict[str, LineType],
    image_shape: Tuple[int],
    working_scale: float # how much smaller the working images ought to be compared to the original image
):

    image_box = BoundingBox(
        0.0, 0.0, 
        float(image_shape[0]), float(image_shape[1])
    )
    geometries = Geometries(image_box)
    geometries.register_surfaces(surfaces)
    geometries.register_polygons(layer_polygons)

    scale_transform = make_scale_transform(working_scale)
    working_geo = geometries.transform(scale_transform)

    raster_stack = working_geo.rasterize()



```