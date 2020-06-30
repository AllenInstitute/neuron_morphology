""" This module contains utilities for running snap_polygons directly from the
Allen Institute's internal Laboratory Information Management System.

Example Usage
-------------
python -m neuron_morphology.snap_polygons
    --host <lims host> 
    --port <lims port> 
    --user <username> 
    --password <password> 
    --database <lims db> 
    --focal_plane_image_series_id 522408212 # for instance
    --image_output_root /some_directory
"""

from typing import Callable, List, Dict, Tuple, Union, Optional
from functools import partial
import os
import warnings
import logging

import marshmallow as mm

from argschema.fields import Int, OutputDir, String
from argschema.sources import ArgSource
from allensdk.internal.core import lims_utilities as lu

from neuron_morphology.snap_polygons.types import (
    NicePathType, ensure_path, ensure_polygon
)


QueryEngineType = Callable[[str], List[Dict]]


def query_for_layer_polygons(
        query_engine: QueryEngineType, 
        focal_plane_image_series_id: int,
        validate_polys: bool = True,
        treatment: str = "Biocytin"
) -> List[Dict[str, Union[NicePathType, str]]]:
    """ Get all layer polygons for this image series

    Parameters
    ----------
    query_engine : executes a query, passed in as a string. Must not require 
        any additional database information.
    focal_plane_image_series_id : used to determine which polygons to fetch
    validate_polys : if True, fail when
        - a label is associated with multiple distinct valid geometries
        - a label is associated with one or more geometries, but none are valid
    treatment: The layer polygons are associated with Biocytin and DAPI 
        treatments. We only need one.

    Returns
    -------
    A collection of labelled polygons.
    """

    query = f"""
        select
            st.acronym as name,
            polygon.path as path,
            polygon.id as polygon_id
        from specimens sp
        join specimens spp on spp.id = sp.parent_id
        join image_series imser on imser.specimen_id = spp.id
        join sub_images si on si.image_series_id = imser.id
        join images im on im.id = si.image_id
        join treatments tm on tm.id = im.treatment_id
        join avg_graphic_objects layer on layer.sub_image_id = si.id
        join avg_group_labels label on label.id = layer.group_label_id
        join avg_graphic_objects polygon on polygon.parent_id = layer.id
        join structures st on st.id = polygon.cortex_layer_id
        where 
            imser.id = {focal_plane_image_series_id}
            and label.name in ('Cortical Layers')
            and tm.name = '{treatment}'
        """
    
    polygons = []
    candidate_names = set()
    found_names: Dict[str, NicePathType] = {}

    for result in query_engine(query):
        name = result["name"]
        path = ensure_path(result["path"])
        poly_id = result["polygon_id"]

        candidate_names.add(name)

        if validate_polys:
            try:
                ensure_polygon(path)
            except (ValueError, TypeError, IndexError):
                warnings.warn(
                    "unable to build shapely object from avg graphic "
                    f"object {poly_id} (label: {name})"
                )
                continue

        if name in found_names:
            if path != found_names[name]:
                if validate_polys:
                    raise ValueError(
                        f"found multiple distinct layer drawings for {name}"
                    )
            else:
                warnings.warn(
                    f"found multiple polygon records for {name} "
                    "(identical paths)"
                )

        polygons.append({
            "name": name,
            "path": path
        })
        found_names[name] = path

    invalid = candidate_names - set(found_names.keys())
    if validate_polys and invalid:
        raise ValueError(f"found only invalid geometries for: {invalid}")

    logging.info("found polygons for %s", found_names.keys())
    return polygons


def query_for_cortical_surfaces(
        query_engine: QueryEngineType,
        focal_plane_image_series_id: int
) -> Tuple[
        Dict[str, Union[NicePathType, str]], 
        Dict[str, Union[NicePathType, str]]
]:
    """ Return the pia and white matter surface drawings for this image series
    """

    query = f"""
        select 
            polygon.path as path,
            label.name as name
        from specimens sp
        join specimens spp on spp.id = sp.parent_id
        join image_series imser on imser.specimen_id = spp.id
        join sub_images si on si.image_series_id = imser.id
        join images im on im.id = si.image_id
        join treatments tm on tm.id = im.treatment_id
        join avg_graphic_objects layer on layer.sub_image_id = si.id
        join avg_graphic_objects polygon on polygon.parent_id = layer.id
        join avg_group_labels label on label.id = layer.group_label_id
        where
            imser.id = {focal_plane_image_series_id}
            and label.name in ('Pia', 'White Matter')
            and tm.name = 'Biocytin'
    """
    results = {}
    for item in query_engine(query):
        results[item["name"]] = {
            "name": item["name"],
            "path": ensure_path(item["path"])
        }
    return results["Pia"], results["White Matter"]
    

def query_for_images(
        query_engine: QueryEngineType, 
        focal_plane_image_series_id: int,
        output_dir: str
) -> List[Dict[str, str]]:
    """ Return Biocytin and DAPI images associated with a focal plane image 
    series
    """

    query = f"""
        select 
            im.jp2, 
            sl.storage_directory,
            tm.name
        from sub_images si 
        join images im on im.id = si.image_id 
        join slides sl on sl.id = im.slide_id 
        join treatments tm on tm.id = im.treatment_id
        where 
            image_series_id = {focal_plane_image_series_id}
            and tm.name in ('Biocytin', 'DAPI')
    """
    results = []
    for image in query_engine(query):
        fname, _ = os.path.splitext(image["jp2"])
        out_fname = f"{image['name']}_{fname}.png"

        results.append({
            "input_path": os.path.join(
                image["storage_directory"], image["jp2"]),
            "output_path": os.path.join(output_dir, out_fname)
        })
    return results


def query_for_image_dims(
        query_engine: QueryEngineType,
        focal_plane_image_series_id: int
) -> Tuple[float, float]:
    """ Find the dimensions of the Biocytin image associated with a focal plane
    image series
    """

    query = f"""
        select 
            im.height as height,
            im.width as width
        from specimens sp
        join specimens spp on spp.id = sp.parent_id
        join image_series imser on imser.specimen_id = spp.id
        join sub_images si on si.image_series_id = imser.id
        join images im on im.id = si.image_id
        join treatments tm on tm.id = im.treatment_id
        where
            imser.id = {focal_plane_image_series_id}
            and tm.name = 'Biocytin'
    """
    result = query_engine(query)
    return result[0]["width"], result[0]["height"]


def get_inputs_from_lims(
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        imser_id: int, 
        image_output_root: Optional[str]
):
    """ Utility for building module inputs from a direct LIMS query
    """

    engine = partial(
        lu.query, 
        host=host, 
        port=port, 
        database=database, 
        user=user, 
        password=password
    )

    layer_polygons = query_for_layer_polygons(engine, imser_id)
    pia_surface, wm_surface = query_for_cortical_surfaces(engine, imser_id)
    image_width, image_height = query_for_image_dims(engine, imser_id)

    results = {
        "layer_polygons": layer_polygons,
        "pia_surface": pia_surface,
        "wm_surface": wm_surface,
        "image_dimensions": {"width": image_width, "height": image_height}
    }

    if image_output_root is not None:
        results["images"] = query_for_images(
            engine, imser_id, image_output_root)

    return results


class PostgresInputConfigSchema(mm.Schema):
    """The parameters required to query a postgres database.
    """

    host = String(
        description="",
        required=True
    )
    database = String(
        description="",
        required=True
    )
    user = String(
        description="",
        required=True
    )
    password = String(
        description="",
        required=False,
        default=os.environ.get("POSTGRES_SOURCE_PASSWORD")
    )
    port = Int(
        description="",
        required=False,  # seems not to get hydrated from the default
        default=5432
    )


class FromLimsSchema(PostgresInputConfigSchema):
    """The parameters required to query LIMS for a set of cortical layer 
    polygons and cortical surface boundaries. 
    """

    focal_plane_image_series_id = Int(
        description="Get inputs for this image series",
        required=True
    )
    image_output_root = OutputDir(
        description="Used to build output paths for associated images",
        required=False,
        default=None,
        allow_none=True
    )


class FromLimsSource(ArgSource):
    """ An alternate argschema source which gets its inputs from lims directly
    """

    ConfigSchema = FromLimsSchema

    def get_dict(self):
        image_output = getattr(self, "image_output_root", None)
        return get_inputs_from_lims(
            self.host,  # pylint: disable=no-member
            self.port,  # pylint: disable=no-member
            self.database,  # pylint: disable=no-member
            self.user,  # pylint: disable=no-member
            self.password,  # pylint: disable=no-member,
            self.focal_plane_image_series_id,  # pylint: disable=no-member
            image_output  # pylint: disable=no-member
        )
