import logging
from functools import partial
from itertools import chain
from multiprocessing import Pool

import numpy as np
import pandas as pd
from shapely.geometry import Polygon, Point, LineString
from scipy.interpolate import CloughTocher2DInterpolator

import argschema as ags
from allensdk.internal.core import lims_utilities as lu
from neuron_morphology.lims_apical_queries import get_data
from neuron_morphology.transforms.pia_wm_streamlines.calculate_pia_wm_streamlines import generate_laplace_field
from neuron_morphology.transforms.geometry import get_vertices_from_two_lines
from neuron_morphology.snap_polygons.__main__ import run_snap_polygons, InputParameters
from neuron_morphology.snap_polygons._from_lims import query_for_layer_polygons, query_for_cortical_surfaces
from neuron_morphology.snap_polygons.types import ensure_linestring, ensure_path
from neuron_morphology.snap_polygons.geometries import Geometries, select_largest_subpolygon
from neuron_morphology.features.layer.reference_layer_depths import DEFAULT_HUMAN_MTG_REFERENCE_LAYER_DEPTHS, DEFAULT_MOUSE_REFERENCE_LAYER_DEPTHS
from neuron_morphology.layered_point_depths.__main__ import step_from_node

logger = logging.getLogger(__name__)

WELL_KNOWN_REFERENCE_LAYER_DEPTHS = {
    "human": DEFAULT_HUMAN_MTG_REFERENCE_LAYER_DEPTHS,
    "mouse": DEFAULT_MOUSE_REFERENCE_LAYER_DEPTHS,
}
class LayerDepthError(Exception):
    pass

def get_cell_soma_data(cell_specimen_ids):
    # based on query in lims_apical_queries but remove requirement of reconstruction
    # there is probably a better way to do this, and should be in neuron_morphology
    ids_str = ', '.join([str(sid) for sid in cell_specimen_ids])
    query_for_soma = f"""
            SELECT DISTINCT sp.id as specimen_id, 'null', layert.name as path_type, poly.path, sc.resolution, 'null', 'null'
            FROM specimens sp
            JOIN biospecimen_polygons AS bsp ON bsp.biospecimen_id=sp.id
            JOIN avg_graphic_objects poly ON poly.id=bsp.polygon_id
            JOIN avg_graphic_objects layer ON layer.id=poly.parent_id
            JOIN avg_group_labels layert ON layert.id=layer.group_label_id
            AND layert.prevent_missing_polygon_structure=false
            JOIN sub_images AS si ON si.id=layer.sub_image_id
            AND si.failed=false
            JOIN images AS im ON im.id=si.image_id
            JOIN slides AS s ON s.id=im.slide_id
            JOIN scans AS sc ON sc.slide_id=s.id
            AND sc.superseded=false
            JOIN treatments t ON t.id = im.treatment_id AND t.id = 300080909 --Why?
            WHERE sp.id IN ({ids_str})
            ORDER BY sp.id
            """
    # all results returned as 'invalid_data' with only soma coords and resolution
    _, cell_data = get_data(query_for_soma)
    soma_centers = {k: cell_data[k]["soma_center"] for k in cell_specimen_ids
                   if cell_data[k]["soma_center"] is not None}
    resolution = cell_data[int(cell_specimen_ids[1])]["resolution"]
    return soma_centers, resolution

def lims_slice_cells_info(query_engine, specimen_ids):
    ids_str = ", ".join([str(s) for s in specimen_ids])
    query = f"""
        select
            sp.id as specimen_id,
            slice.id as slice_id,
            image_series.id as image_series_id
        from specimens sp
        join specimens slice on slice.id = sp.parent_id
        join image_series on image_series.specimen_id=slice.id
        where image_series.type='FocalPlaneImageSeries'
        and sp.id in ({ids_str})
    """
    results = query_engine(query)
    return results

def query_for_soma_centers(query_engine, cell_specimen_ids):
    """Return soma center coordinates for a list of specimens in a single image,
    converted to microns (along with the resolution).
    """
    ids_str = ', '.join([str(sid) for sid in cell_specimen_ids])

    query = f"""
        select distinct
            polygon.path as path,
            label.name as name,
            sc.resolution as resolution,
            bsp.biospecimen_id as specimen_id
        from specimens sp
        join specimens spp on spp.id = sp.parent_id
        join image_series imser on imser.specimen_id = spp.id
        join sub_images si on si.image_series_id = imser.id
        join images im on im.id = si.image_id
        join slides s on s.id=im.slide_id
        join scans sc on sc.slide_id=s.id
        join treatments tm on tm.id = im.treatment_id
        join avg_graphic_objects layer on layer.sub_image_id = si.id
        join avg_graphic_objects polygon on polygon.parent_id = layer.id
        join avg_group_labels label on label.id = layer.group_label_id
        join biospecimen_polygons bsp on bsp.polygon_id = polygon.id
        where
            label.name = 'Soma'
            and tm.name = 'Biocytin'
            and bsp.biospecimen_id in ({ids_str})
    """
    results = query_engine(query)
    soma_centers = {}
    if len(results)==0:
        raise ValueError('No soma centers found.')
    for item in results:
        resolution = item["resolution"]
        path = ensure_path(item["path"])
        soma_centers[item["specimen_id"]] = np.asarray(path).mean(axis=0)*resolution
    return soma_centers, resolution

def trim_layers(layer_polygons, pia_surface, wm_surface,
                multipolygon_error_threshold=100, **kwargs):
    """Follow the snap_polygons approach to trim a list of layer polygons to lie
    within the bounds of a pia/wm-defined region."""
    if pia_surface is None or wm_surface is None:
        raise ValueError("Missing pia/wm.")
    geometries = Geometries()
    geometries.register_polygons(layer_polygons)
    geometries.register_surface("pia", pia_surface["path"])
    geometries.register_surface("wm", wm_surface["path"])
    pia_wm_vertices = get_vertices_from_two_lines(
        pia_surface['path'], wm_surface['path'])
    bounds = Polygon(pia_wm_vertices)

    multipolygon_resolver = partial(
        select_largest_subpolygon,
        error_threshold=multipolygon_error_threshold
    )

    result_geos = geometries.cut(bounds, multipolygon_resolver=multipolygon_resolver)
    return result_geos.to_json()

def layer_info_from_snap_polygons_output(output, resolution=1):
    layers = {}
    pia_path = None
    wm_path = None
    for polygon in output["polygons"]:
        layers[polygon['name']] = {'bounds': Polygon(resolution*np.array(polygon['path']))}
    for surface in output["surfaces"]:
        name = surface['name']
        path = list(resolution*np.array(surface['path']))
        if name=='pia':
            pia_path = path
        elif name=='wm':
            wm_path = path
        else:
            path = LineString(path)
            layer, side = name.split('_')
            layers[layer][f"{side}_surface"] = path
    return layers, pia_path, wm_path

def get_missing_layer_info(layers, species, infer_missing_layers=True):
    ref_layer_depths = WELL_KNOWN_REFERENCE_LAYER_DEPTHS[species].copy()
    # don't want to include wm as a layer!
    ref_layer_depths.pop('wm')
    all_layers_ordered = sorted(ref_layer_depths.keys())
    complete_layers = sorted((
        layer.replace("Layer", '') for layer, layer_poly in layers.items()
        if 'pia_surface' in layer_poly and 'wm_surface' in layer_poly
    ))
    if not complete_layers:
        raise LayerDepthError("No layer boundaries found.")
    first = complete_layers[0]
    last = complete_layers[-1]
    top_path = layers[f"Layer{first}"]['pia_surface']
    top_path = list(top_path.coords)
    bottom_path = layers[f"Layer{last}"]['wm_surface']
    bottom_path = list(bottom_path.coords)
    missing_above = all_layers_ordered[:all_layers_ordered.index(first)]
    missing_below = all_layers_ordered[all_layers_ordered.index(last)+1:]
    pia_extra_dist = wm_extra_dist = 0
    if len(missing_above) > 0:
        if infer_missing_layers:
            pia_extra_dist = sum(ref_layer_depths[layer].thickness for layer in missing_above)
        else:
            pia_extra_dist = np.nan
    wm_extra_dist = sum(ref_layer_depths[layer].thickness for layer in missing_below)
    if len(missing_below) > 0:
        if infer_missing_layers:
            wm_extra_dist = sum(ref_layer_depths[layer].thickness for layer in missing_below)
        else:
            wm_extra_dist = np.nan
    return top_path, bottom_path, pia_extra_dist, wm_extra_dist

def get_layer_for_point(point, layer_polys):
    in_layer = [
        layer for layer in layer_polys if
        layer_polys[layer]['bounds'].intersects(Point(*point))
        # checks for common boundary or interior
    ]

    if len(in_layer) == 0:
        raise LayerDepthError("Point not found in any layer")
    elif len(in_layer) == 1:
        layer_name = in_layer[0]
    else:
        # overlap means point is likely on a boundary
        # choose upper layer, avoiding L1
        for layer in sorted(in_layer):
            if not layer=="Layer1":
                layer_name = layer
        logger.warning(f"Overlapping layers: {in_layer}. Choosing {layer_name}")
    layer_poly = layer_polys[layer_name]
    return layer_name, layer_poly

def get_layer_depths(point, layer_polys, pia_path, wm_path, depth_interp, dx_interp, dy_interp,
                     step_size=1.0, max_iter=1000,
                     pia_extra_dist=0, wm_extra_dist=0):

    def dist_to_boundary(boundary_path, direction):
        try:
            _, dist = step_from_node(
                point, depth_interp, dx_interp, dy_interp,
                boundary_path, direction*step_size, max_iter, adaptive_scale=1
            )
        except ValueError as e:
            logger.warning(e)
            dist = np.nan
        return dist

    layer_name, layer_poly = get_layer_for_point(point, layer_polys)
    if pia_path is not None:
        pia_path = ensure_linestring(pia_path)
        pia_distance = dist_to_boundary(pia_path, 1)
    else:
        pia_distance = np.nan
    if wm_path is not None:
        wm_path = ensure_linestring(wm_path)
        wm_distance = dist_to_boundary(wm_path, -1)
    else:
        wm_distance = np.nan
    if 'pia_surface' in layer_poly:
        pia_side_dist = dist_to_boundary(layer_poly['pia_surface'], 1)
    else:
        pia_side_dist = dist_to_boundary(layer_poly['bounds'].boundary, 1)
    if 'wm_surface' in layer_poly:
        wm_side_dist = dist_to_boundary(layer_poly['wm_surface'], -1)
    else:
        wm_side_dist = dist_to_boundary(layer_poly['bounds'].boundary, -1)
    pia_distance += pia_extra_dist
    wm_distance += wm_extra_dist

    layer_thickness = wm_side_dist + pia_side_dist
    cortex_thickness = pia_distance + wm_distance
    out = {
        'layer_depth': pia_side_dist,
        'layer_thickness': layer_thickness,
        'normalized_layer_depth': pia_side_dist/layer_thickness,
        'normalized_depth': pia_distance/cortex_thickness, #vs depth_interp(point)?
        'absolute_depth': pia_distance,
        'cortex_thickness': cortex_thickness,
        'wm_distance': wm_distance,
        'layer':layer_name,
        }
    return out

def resample_line(coords, distance_delta=50):
    line = LineString(coords)
    distances = np.arange(0, line.length, distance_delta)
    points = [line.interpolate(distance) for distance in distances] + [line.boundary[1]]
    line_coords = [point.coords[0] for point in points]
    return line_coords

def get_depths_from_processed_layers(layers, pia_path, wm_path, soma_centers,
                                     step_size=2.0, max_iter=1000,
                                     species=None, orient_by_layer_bounds=False,
                                     infer_missing_layers=True
                                     ):
    """Get depths (within-layer and absolute) for a list of soma positions,
    given processed layer and pia/wm records.

    The key difference from the layered_point_depths approach is to not require
    annotated pia_surface/wm_surface for each layer. Instead you just need the
    pia/wm for up/down orientation and use the whole polygon as a boundary."""
    errors = []
    try:
        top_path = pia_path
        bottom_path = wm_path
        pia_extra_dist = wm_extra_dist = 0
        if (pia_path is None) or (wm_path is None):
            if not orient_by_layer_bounds:
                raise ValueError("Pia or WM is missing, can't find depths.")
            top_path, bottom_path, pia_extra_dist, wm_extra_dist = get_missing_layer_info(
                layers, species, infer_missing_layers=infer_missing_layers)

        top_path = resample_line(top_path)
        bottom_path = resample_line(bottom_path)

        (_, _, _, mesh_coords, mesh_values, mesh_gradients) = generate_laplace_field(
                top_path,
                bottom_path,
                )
        interp = CloughTocher2DInterpolator
        depth_interp = interp(mesh_coords, mesh_values)
        dx_interp = interp(mesh_coords, mesh_gradients[:,0])
        dy_interp = interp(mesh_coords, mesh_gradients[:,1])
    except LayerDepthError as exc:
        top_path = bottom_path = None
        pia_extra_dist = wm_extra_dist = np.nan
        depth_interp = dx_interp = dy_interp = lambda x: np.nan
        logger.error(exc)
        errors.append(str(exc))

    outputs = {}
    cell_errors = {}
    for name, point in soma_centers.items():
        try:
            outputs[name] = get_layer_depths(
                point, layers, top_path, bottom_path, depth_interp, dx_interp, dy_interp,
                step_size=step_size, max_iter=max_iter,
                pia_extra_dist=pia_extra_dist, wm_extra_dist=wm_extra_dist
                )
        except (LayerDepthError,) as exc:
            error = f"Failure getting depth info for cell {name}: {exc}"
            logger.error(error)
            cell_errors[name] = str(exc)
    if ((len(layers) >= 3) | ((pia_path is not None) & (wm_path is not None))):
        if len(soma_centers) == len(cell_errors):
            raise ValueError(f"All cells in slice failed unexpectedly: {cell_errors}")
    return outputs, errors, cell_errors

def run_layer_depths(image_series_id, cell_specimen_ids, species=None, grouped_cells=True,
                     use_snap_polygons_boundaries=False, infer_missing_layers=True):
    if grouped_cells:
        try:
            layer_polygons = query_for_layer_polygons(lu.query, image_series_id)
            pia_surface, wm_surface = query_for_cortical_surfaces(lu.query, image_series_id)
        except ValueError:
        # error may be from multiple pia/wm drawings, running cells individually
        # lets them each find the correct drawing
            slice_records = chain.from_iterable(
                [run_layer_depths(image_series_id, [specimen_id], grouped_cells=False)
                 for specimen_id in cell_specimen_ids]
            )
            return slice_records
    else:
        layer_polygons = query_for_layer_polygons(lu.query, image_series_id, validate_polys=False)
        pia_surface, wm_surface = query_for_cortical_surfaces(
            lu.query, image_series_id, cell_specimen_id=cell_specimen_ids[0]
        )

    try:
        soma_centers, resolution = query_for_soma_centers(lu.query, cell_specimen_ids)
        if use_snap_polygons_boundaries:
            input_data=dict(layer_polygons=layer_polygons, pia_surface=pia_surface, wm_surface=wm_surface)
            args = InputParameters().load(input_data)
            args.pop('log_level')
            output = run_snap_polygons(**args)
        else:
            # trim layers to pia/wm bounds (subset of snap_polygons process)
            # helps run streamlines in L1, in case boundary extends slightly above pia
            output = trim_layers(layer_polygons, pia_surface, wm_surface)
        layers, pia_path, wm_path = layer_info_from_snap_polygons_output(output, resolution)

        slice_results, slice_errors, cell_errors = get_depths_from_processed_layers(
            layers, pia_path, wm_path, soma_centers, species=species, max_iter=4000,
            orient_by_layer_bounds=use_snap_polygons_boundaries,
            infer_missing_layers=infer_missing_layers)

        slice_records = [dict(specimen_id=specimen_id, image_series_id=image_series_id,
                              errors=slice_errors, **results)
                        for specimen_id, results in slice_results.items()]
        missing_records = [dict(specimen_id=specimen_id, image_series_id=image_series_id,
                              errors="Missing soma center")
                        for specimen_id in cell_specimen_ids if specimen_id not in soma_centers]
        error_records = [dict(specimen_id=specimen_id, image_series_id=image_series_id, errors=err)
                        for specimen_id, err in cell_errors.items()]
        slice_records += missing_records + error_records
    except ValueError as exc:
        logging.warning(f'Failed to get depths: image series {image_series_id}. {exc}')
        slice_records = [dict(specimen_id=specimen_id, image_series_id=image_series_id,
                              errors=str(exc))
                        for specimen_id in cell_specimen_ids]
    except Exception as exc:
        logging.exception(f'Failed to get depths: image series {image_series_id}')
        slice_records = [dict(specimen_id=specimen_id, image_series_id=image_series_id,
                              errors=repr(exc))
                        for specimen_id in cell_specimen_ids]
    return slice_records

def main(input_file, output_file, **kwargs):
    cells = pd.read_csv(input_file, index_col=0).index

    df = pd.DataFrame.from_records(lims_slice_cells_info(lu.query, cells))
    cell_groups = df.groupby('image_series_id')['specimen_id'].apply(list)
    image_series_ids = cell_groups.index.values
    cell_specimen_ids = cell_groups.values

    pool = Pool()
    fcn = partial(run_layer_depths, **kwargs)
    results = pool.starmap(fcn, zip(image_series_ids, cell_specimen_ids))

    depth_df = pd.DataFrame.from_records(chain(*results))
    depth_df.to_csv(output_file, index=False)

class SomaLayerDepthSchema(ags.ArgSchema):
    input_file = ags.fields.InputFile(
        description="input cell list as a csv with the specimen ids in the first column"
    )
    output_file = ags.fields.OutputFile(default="soma_depths.csv")
    use_snap_polygons_boundaries = ags.fields.Boolean(default=False)

if __name__ == "__main__":
    module = ags.ArgSchemaParser(schema_type=SomaLayerDepthSchema)
    module.args.pop("log_level")
    # logger.setLevel(module.args.pop("log_level"))
    main(**module.args)
