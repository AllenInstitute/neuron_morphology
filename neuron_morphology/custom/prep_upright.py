import sys
import psycopg2
import psycopg2.extras
sys.path.append("/home/keithg/allen/neuron_morphology/")
import neuron_morphology.swc as swc

########################################################################
# LIMS emulation layer

cursor = None

def fetch_json(specimen_id):
    sql = """
        SELECT DISTINCT
                sp.id as specimen_id, 
                sp.storage_directory, 
                wkf.filename, 
                sp.cell_depth,
                agl.name AS drawing_layer, 
                polygon.id AS polygon_id, 
                polygon.path,
                sc.resolution
        FROM specimens sp JOIN specimens spp ON spp.id=sp.parent_id
            JOIN neuron_reconstructions nr 
                ON nr.specimen_id = sp.id
                AND nr.superseded=False
            JOIN well_known_files wkf 
                ON wkf.attachable_id=nr.id
            JOIN well_known_file_types wkft 
                ON wkft.id = wkf.well_known_file_type_id
                AND wkft.name = '3DNeuronReconstruction'
            JOIN image_series iser 
                ON iser.specimen_id=spp.id 
                AND iser.type = 'FocalPlaneImageSeries' 
                AND iser.is_stack = 'f'
            JOIN sub_images si 
                ON si.image_series_id=iser.id
            JOIN avg_graphic_objects layer 
                ON layer.sub_image_id=si.id
            JOIN avg_graphic_objects polygon 
                ON polygon.parent_id=layer.id
            JOIN avg_group_labels agl 
                ON layer.group_label_id=agl.id
            JOIN images im 
                ON im.id=si.image_id
                AND (im.treatment_id IS null 
                OR im.treatment_id = 300080909) --;"Biocytin"
            JOIN image_types imt 
                ON imt.id=im.image_type_id
            JOIN scans sc 
                ON sc.slide_id=im.slide_id
            JOIN biospecimen_polygons bp 
                ON bp.polygon_id = polygon.id
        WHERE agl.name IN ('Soma', 'White Matter', 'Pia')
        AND bp.biospecimen_id = sp.id
        AND sp.id = %s
    """
    stmt = sql % specimen_id
    cursor.execute(stmt)
    res = cursor.fetchall()
#    if len(res) > 3:
#        print "WARNING: too many polygons returned. Expected 3, got %d"%len(res)
#        for blk in res:
#            print blk
#        print("--------------------")
#    # find first soma, pia and white matter entries
#    jout = {}
#    for blk in res:
#        name = blk['drawing_layer']
#        if 'Soma' not in jout and name == 'Soma':
#            jout[name] = {}
#            jout[name]["path"] = blk['path']
#            jout[name]["resolution"] = blk["resolution"]
#        elif 'Pia' not in jout and name == 'Pia':
#            jout[name] = {}
#            jout[name]["path"] = blk['path']
#            jout[name]["resolution"] = blk["resolution"]
#        elif 'White Matter' not in jout and name == 'White Matter':
#            jout[name] = {}
#            jout[name]["path"] = blk['path']
#            jout[name]["resolution"] = blk["resolution"]
#    if len(jout) != 3:
#        print stmt
#        print jout
#        raise Exception("Failed to fetch necessary path -- got %d of 3" % len(jout))
#    jout["swc_file"] = res[0]['storage_directory'] + res[0]['filename']
    if len(res) != 3:
        print "ERROR: Too many polygons. Expected 3, got %d" % len(res)
        print specimen_id
        print stmt
        for blk in res:
            print blk
        raise Exception("fubar")
    jout = {}
    jout["swc_file"] = res[0]['storage_directory'] + res[0]['filename']
    for blk in res:
        name = blk['drawing_layer']
        jout[name] = {}
        jout[name]["path"] = blk['path']
        jout[name]["resolution"] = blk["resolution"]
#
    return jout


########################################################################
# library code

import math
import argparse
import sys
import numpy as np
from scipy.spatial.distance import euclidean
import allensdk.core.json_utilities as json

def calculate_centroid(x, y):
    ''' Calculates the center of a polygon, using weighted averages
    of vertex locations
    '''
    assert len(x) == len(y), "Vertex arrays are of incorrect shape"
    tot_len = 0.0
    tot_x = 0.0
    tot_y = 0.0
    for i in range(len(x)):
        x0 = x[i-1]
        y0 = y[i-1]
        x1 = x[i]
        y1 = y[i]
        seg_len = math.sqrt((x1-x0)*(x1-x0) + (y1-y0)*(y1-y0))
        tot_len += seg_len
        tot_x += seg_len * x0
        tot_x += seg_len * x1
        tot_y += seg_len * y0
        tot_y += seg_len * y1
    tot_x /= 2.0 * tot_len
    tot_y /= 2.0 * tot_len
    return tot_x, tot_y


def get_pia_wm_rotation_transform(soma_coords, wm_coords, pia_coords, resolution):
    soma_x, soma_y = convert_coords_str(soma_coords)

    # get soma position using weighted average of vertices
    avg_soma_position = calculate_centroid(soma_x, soma_y)

    pia_proj = project_to_polyline(pia_coords, avg_soma_position)
    wm_proj = project_to_polyline(wm_coords, avg_soma_position)
    theta = vector_angle((0, 1), pia_proj - wm_proj)

    tr_rot = [np.cos(theta), np.sin(theta), 0,
              -np.sin(theta), np.cos(theta), 0,
              0, 0, 1,
              0, 0, 0
             ]
    return tr_rot, resolution * euclidean(avg_soma_position, pia_proj)


def convert_coords_str(coord_str):
    vals = coord_str.split(',')
    x = np.array(vals[0::2], dtype=float)
    y = np.array(vals[1::2], dtype=float)
    return x, y


def dist_proj_point_lineseg(p, q1, q2):
    # based on c code from http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
    l2 = euclidean(q1, q2) ** 2
    if l2 == 0:
        return euclidean(p, q1) # q1 == q2 case
    t = max(0, min(1, np.dot(p - q1, q2 - q1) / l2))
    proj = q1 + t * (q2 - q1)
    return euclidean(p, proj), proj


def project_to_polyline(boundary, soma):
    x, y = convert_coords_str(boundary)
    points = zip(x, y)
    dists_projs = [dist_proj_point_lineseg(soma, np.array(q1), np.array(q2))
                 for q1, q2 in zip(points[:-1], points[1:])]
    min_idx = np.argmin(np.array([d[0] for d in dists_projs]))
    return dists_projs[min_idx][1]


def vector_angle(v1, v2):
    return np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])


########################################################################
# pipeline code

def calculate_transform(db_conn, specimen_id):
    global cursor

    cursor = db_conn

    jin = fetch_json(specimen_id)
    soma = jin["Soma"]["path"]
    pia = jin["Pia"]["path"]
    wm = jin["White Matter"]["path"]
    res = jin["Pia"]["resolution"]

    tr_rot, depth = get_pia_wm_rotation_transform(wm_coords=wm, pia_coords=pia, soma_coords=soma, resolution=res)

    morph = swc.read_swc(jin["swc_file"])
    morph.apply_affine(tr_rot)
    root = morph.soma_root()
    tr_rot[ 9] = -root.x
    tr_rot[10] = -root.y - depth
    tr_rot[11] = -root.z

    return tr_rot

