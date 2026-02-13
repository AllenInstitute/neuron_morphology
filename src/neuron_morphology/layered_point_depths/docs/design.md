Layered Point Depths Design
===========================

This is a standalone executable which takes as inputs:
- an swc file describing a neuron's morphology
- a set of 2D polylines describing boundaries between cortical layers
- a gradient field describing the local pia -> white matter direction on a grid

These local directions define a streamline from pia -> white matter for each point in the field.

and outputs:
- For each node in the morphology: 
    - the depth of that node following the its streamline
    - the label of the layer containing that node
    - the intersection of that node's streamline and the piawise and whitematterwise boundaries of the node's containing layer.
- optionally, debug plots showing these streamlines for each node

Out of scope, but might be required by future work:
- solving this problem in 3d
- accepting a wider array of transform types as inputs

#### approach

Algorithmically, we will:

1. build shapely polygons from the layer boundaries
2. build interpolators from the gradient field
3. for each node in the morphology:
    - ask which layer polygon contains that node
    - step along the interpolated gradient field, checking whether we have left the containing layer and recording distance traveled.
    - if we have, check the intersection of the ray defined by the last step with the layer polygon. That is our pia / wm side intersection.
    - if traveling piaward, continue stepping until we cross pia.

This is pretty simple, and ought to be fast due to reliance on shapely's c-implemented containment checks (which I believe are raycasting and counting intersections). It is also embarrasingly parallel.

Some downsides / alternatives:
- We might step off of our streamline
    - We can mitigate this with small step sizes
    - alternatively: input is a depth field and we use scipy.integrate.RK45 or similar to walk through it.
- We're doing unnecessary intersection checks: we really only care if stepping in the piaward direction intersects with the piaward surface of a layer
    - as a minor optimization we could check containment for the first point, then directed intersection on later points.
- If the layer drawings are too short, we could step out to the sides
    - if the neuron extends past the layer drawings, we might want to reject these layer drawings!
    - we can attempt to extend the layer drawings (ideally in a separate executable)
- extending to 3d might be hard. Shapely in particular does not support 3d.

#### design

```Python


class GradientStepper:

    # if we choose to use rk, we can argue the depth field instead
    def __init__(
        self, 
        gradient_field: np.ndarray, 
        get_node_position: Callable[[Dict], Tuple[float, float]]):
        """ 

        Parameters
        ----------
        gradient_field : A 2xshape[0]xshape[1] array of gradient vectors
        get_node_positions : Takes a node and returns 2 coordinates, ordered as in gradient_field

        """

    def build_interpolators(self):
        """ Setup interpolators for this stepper's gradient field
        """

    def walk(
        self, 
        start: Tuple[float, float], 
        step_size: float,
        max_steps: int,
        visitor: Callable[
            [Tuple[float, float], Tuple[float, float]], 
            bool
        ]
    ) -> List[Tuple[float, float]]:
        """ Traverses an (interpolated) gradient field. Records visited points and calls a visitor at each point to determine if the walk should stop. The visitor is called with the previous point and the current point
        """

# probably users want to argue the layers once to a factory and then call that to get a bunch of visitors
class LayerVisitor:

    def __init__(self, layers: Dict[str, shapely.polygon.Polygon]):
        """ Suitable for GradientStepper.

        Parameters
        ----------
        layers : each defines the entire exterior boundary of a layer.

        """

    def __call__(
        self, 
        last_position: Tuple[float, float],
        current_position: Tuple[float, float]
    ) -> bool:
        """ Stores an array of positions and contianing layers. If the layer changes, stores the intersection of the change with the step. If the 
        current position is outside of all layers, return False, otherwise True.
        """


def load_field(path: str) 
    -> Tuple[
        np.ndarray, 
        Callable[[Dict], Tuple[float, float]]
    ]:
    """ Reads a netcdf file containing a gradient field. Returns the field as a 
    2xdim_1xdim_2 array and a function which extracts ordered positions from morphology nodes.
    """


def layered_depths_for_point(node: Dict,) -> Dict:
    """ Given a node, find its layer, depth, and intersection depths.
    """

def layer_polys_from_boundaries(
    boundaries: Dict[str, Sequence[Tuple[float, float]]]
) -> Dict[str, shapely.polygon.Polygon]:
    """ Constructs closed polygons from boundaries
    """


def main(
    swc_path: str,
    field_path: str,
    layer_boundaries: Dict[str, Sequence[Tuple[float, float]]],
    output_path: str
):

    gradient_field, get_node_position = load_field(field_path)
    morphology = morphology_from_swc(swc_path)
    layers = layer_polys_from_boundaries(layer_boundaries)

    outputs = []

    for node in morphology.nodes():
        outputs.append(layered_depths_for_point(
            node, get_node_position, gradient_field, layers
        ))

    depths = LayeredPointDepths.from_dataframe(pd.DataFrame(outputs))
    depths.to_csv(output_path)


```

#### testing



#### presentation

