from typing import Callable, List, Dict, Tuple


QueryEngineType = Callable[[str], List[Dict]]
PathType = List[List[float]]
PathsType = Dict[str, PathType]


def query_for_layer_polygons(
    query_engine: QueryEngineType, 
    focal_plane_image_series_id: int
    ) -> PathsType:
    """
    """


def query_for_cortical_surfaces(
    query_engine: QueryEngineType,
    focal_plane_image_series_id: int
) -> Tuple[PathType, PathType]:
    """
    """


def query_for_image_dims(
    query_engine: QueryEngineType,
    focal_plane_image_series_id: int
) -> Tuple[float, float]:
    """
    """


def get_inputs_from_lims(args):
    """ Utility for building module inputs from a direct LIMS query
    """

    imser_id = args.if_from_lims.focal_plane_image_series_id

    # need pg8000 for this, not otherwise
    from allensdk.internal.core import lims_utilities as lu

    layer_polygons = query_for_layer_polygons(lu.query, imser_id)
    pia_surface, wm_surface = query_for_cortical_surfaces(lu.query, imser_id)
    image_width, image_height = query_for_image_dims(lu.query, imser_id)

    return {
        "layer_polygons": layer_polygons,
        "pia_surface": pia_surface,
        "wm_surface": wm_surface,
        "image_dimensions": {"width": image_width, "height": image_height}
    }