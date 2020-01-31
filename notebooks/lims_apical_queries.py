import os
import psycopg2
import numpy as np


def convert_coords_str(coords_str: str, resolution=None):
    """Convert a comma seperated string of coordinate pairs"""
    vals = coords_str.split(',')

    if resolution:
        resolution = float(resolution)
    else:
        resolution = 1.0

    x = np.asarray(vals[0::2], dtype=float) * resolution
    y = np.asarray(vals[1::2], dtype=float) * resolution
    coords = {'x': x, 'y': y}

    return coords


def get_data(query):
    host = os.getenv("DBHOST")
    dbname = os.getenv("DBNAME")
    user = os.getenv("DBREADER")
    password = os.getenv("DBPASSWORD")
    conn_str = f'host={host} dbname={dbname} user={user} password={password}'

    data = {}
    with psycopg2.connect(conn_str) as conn:
        conn.set_session(readonly=True)
        with conn.cursor() as curs:
            curs.execute(query)
            for row in curs:
                (specimen_id, apical_tag, path_type,
                 path_str, resolution, swc_dir, swc_name) = row
                if specimen_id not in data:
                    data[specimen_id] = {'apical_tag': apical_tag,
                                         'resolution': resolution,
                                         'swc_file': os.path.join(swc_dir, swc_name),
                                         'soma_path_str': None,
                                         'soma_center': None,
                                         'soma_center_pix': None,
                                         'pia_path_str': None,
                                         'pia_coords': None,
                                         'wm_path_str': None,
                                         'wm_coords': None,
                                         }
                if path_type == 'Soma':
                    data[specimen_id]['soma_path_str'] = path_str
                    soma_coords = convert_coords_str(path_str,  resolution=data[specimen_id]['resolution'])
                    data[specimen_id]['soma_center'] = np.asarray(
                        (soma_coords['x'].mean(), soma_coords['y'].mean()))
                    soma_pix_coords = convert_coords_str(path_str)
                    data[specimen_id]['soma_center_pix'] = np.asarray(
                        (soma_pix_coords['x'].mean(), soma_pix_coords['y'].mean()))
                elif path_type == 'Pia':
                    data[specimen_id]['pia_path_str'] = path_str
                    data[specimen_id]['pia_coords'] = convert_coords_str(path_str, resolution=data[specimen_id]['resolution'])
                elif path_type == 'White Matter':
                    data[specimen_id]['wm_path_str'] = path_str
                    data[specimen_id]['wm_coords'] = convert_coords_str(path_str, resolution=data[specimen_id]['resolution'])

    invalid_ids = []
    for sid, sdata in data.items():
        if (sdata['soma_path_str'] is None or
                sdata['pia_path_str'] is None or
                sdata['wm_path_str'] is None):

            invalid_ids.append(sid)

    invalid_data = {sid: data.pop(sid) for sid in invalid_ids}
    return data, invalid_data


def get_all_intact_apical():
    query = """
        SELECT DISTINCT sts.specimen_id as specimen_id, specimen_tags.name, layert.name as path_type, poly.path, sc.resolution, wkf.storage_directory, wkf.filename
        FROM specimen_tags_specimens AS sts
        JOIN specimen_tags ON specimen_tags.id=sts.specimen_tag_id
        AND specimen_tags.name IN ('apical - intact')
        JOIN biospecimen_polygons AS bsp ON bsp.biospecimen_id=sts.specimen_id
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
        JOIN neuron_reconstructions AS nr ON nr.specimen_id=sts.specimen_id
        AND nr.superseded=false
        JOIN well_known_files AS wkf ON wkf.attachable_id=nr.id
        AND wkf.attachable_type='NeuronReconstruction'
        JOIN well_known_file_types AS wkft on wkft.id=well_known_file_type_id
        AND wkft.name='3DNeuronReconstruction'
        ORDER BY sts.specimen_id
    """
    return get_data(query)


def get_benchmark_apical():
    # From Nathan Gouwens
    # neurons with m-type SPINY 3,4,5,7,8,9,10,11,12,13,14,16,17
    specimen_ids = [
     313862022, 314642645, 314804042, 314822529, 314831019, 314900022, 318733871,
     318808427, 320207387, 320668879, 321906005, 323865917, 324025297, 324025371,
     324521027, 325941643, 329550137, 348592897, 349621141, 354190013, 354833767,
     370351753, 382982932, 386049446, 386970660, 395830185, 397351623, 397353539,
     422738880, 466632464, 467703703, 468120757, 468193142, 469704261, 469793303,
     469798159, 471129934, 471141261, 471143169, 471758398, 471767045, 471786879,
     471789504, 471800189, 473020156, 473601979, 473611755, 475459689, 475744706,
     476048909, 476049169, 476054887, 476086391, 476126528, 476131588, 476135066,
     476216637, 476218657, 476263004, 476451456, 476455864, 476457450, 476562817,
     476616076, 476823462, 477127614, 477135941, 478497530, 478586295, 478888052,
     478892782, 479010903, 479013100, 479179020, 479225052, 479225080, 479704527,
     479721491, 479728896, 479770916, 480003970, 480087928, 480114344, 480116737,
     480122859, 480124551, 480169178, 480351780, 480353286, 483020137, 483061182,
     483068687, 483092310, 484564503, 484679812, 485161419, 485468180, 485574721,
     485574832, 485835016, 485835055, 485836906, 485837504, 485838981, 485880739,
     485909730, 485912047, 485931158, 486025194, 486052980, 486110216, 486111903,
     486132712, 486146717, 486239338, 486502127, 486893033, 487601493, 487664663,
     488117124, 488420599, 488679042, 488680917, 488683425, 488695444, 488697163,
     488698341, 490205998, 490259231, 490485142, 490916882, 497611660, 501799874,
     501847931, 501956013, 502267531, 502269786, 502366405, 502614426, 502978383,
     502999078, 503286448, 503814817, 507101551, 507918877, 509003464, 510658021,
     513800575, 515249852, 515524026, 515986607, 517077548, 521938313, 524850271,
     527826878, 555241875, 556369531, 557037024, 557203722, 557252022, 557864274,
     557874460, 557998843, 560678143, 563350008, 566506157, 568568071, 569653118,
     588402092, 588419063, 588712191, 589128331, 589427435, 589442285, 589760138,
     598628992, 599334696, 602822298, 607124114, 656411052, 656421538, 656425408,
     656658253, 656707861, 676322245, 698217104, 698226504, 698230720, 698235442,
     698237629
     ]

    ids_str = ', '.join([str(sid) for sid in specimen_ids])

    query = f"""
        SELECT DISTINCT sts.specimen_id as specimen_id, specimen_tags.name, layert.name as path_type, poly.path, sc.resolution, wkf.storage_directory, wkf.filename
        FROM specimen_tags_specimens AS sts
        JOIN specimen_tags ON specimen_tags.id=sts.specimen_tag_id
        AND sts.specimen_id IN ({ids_str})
        AND specimen_tags.name IN ('apical - intact')
        JOIN biospecimen_polygons AS bsp ON bsp.biospecimen_id=sts.specimen_id
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
        JOIN neuron_reconstructions AS nr ON nr.specimen_id=sts.specimen_id
        AND nr.superseded=false
        JOIN well_known_files AS wkf ON wkf.attachable_id=nr.id
        AND wkf.attachable_type='NeuronReconstruction'
        JOIN well_known_file_types AS wkft on wkft.id=well_known_file_type_id
        AND wkft.name='3DNeuronReconstruction'
        ORDER BY sts.specimen_id
        """
    return get_data(query)
