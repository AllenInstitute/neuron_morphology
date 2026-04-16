# Vendored from allensdk.internal.core.lims_utilities (AllenInstitute/AllenSDK).
# Original: Allen Institute Software License (2-clause BSD + non-commercial clause).
# Copyright 2017. Allen Institute. All rights reserved.
#
# Modifications: removed allensdk dependency; read_url_get is now imported
# from neuron_morphology.util.json_utilities.

import os
import platform
import re
import logging

from neuron_morphology.util.json_utilities import read_url_get

HDF5_FILE_TYPE_ID = 306905526
NWB_FILE_TYPE_ID = 475137571
NWB_UNCOMPRESSED_FILE_TYPE_ID = 478840678
NWB_DOWNLOAD_FILE_TYPE_ID = 481007198
METHOD_CONFIG_FILE_TYPE_ID = 324440685
MODEL_PARAMETERS_FILE_TYPE_ID = 329230374
BIOPHYS_MODEL_PARAMETERS_FILE_TYPE_ID = 329230374


def get_well_known_files_by_type(wkfs, wkf_type_id):
    out = [
        os.path.join(wkf["storage_directory"], wkf["filename"])
        for wkf in wkfs
        if wkf.get("well_known_file_type_id", None) == wkf_type_id
    ]
    if not out:
        raise IOError(
            "Could not find well known files with type %d." % wkf_type_id
        )
    return out


def get_well_known_file_by_type(wkfs, wkf_type_id):
    out = get_well_known_files_by_type(wkfs, wkf_type_id)
    if len(out) != 1:
        raise IOError(
            "Expected single well known file with type %d. Got %d."
            % (wkf_type_id, len(out))
        )
    return out[0]


def get_well_known_files_by_name(wkfs, filename):
    out = [
        os.path.join(wkf["storage_directory"], wkf["filename"])
        for wkf in wkfs
        if wkf["filename"] == filename
    ]
    if not out:
        raise IOError(
            "Could not find well known files with name %s." % filename
        )
    return out


def get_well_known_file_by_name(wkfs, filename):
    out = get_well_known_files_by_name(wkfs, filename)
    if len(out) != 1:
        raise IOError(
            "Expected single well known file with name %s. Got %d."
            % (filename, len(out))
        )
    return out[0]


def append_well_known_file(wkfs, path, wkf_type_id=None, content_type=None):
    record = {
        "filename": os.path.basename(path),
        "storage_directory": os.path.dirname(path),
    }
    if wkf_type_id is not None:
        record["well_known_file_type_id"] = wkf_type_id
    if content_type is not None:
        record["content_type"] = content_type

    for wkf in wkfs:
        if wkf["filename"] == record["filename"]:
            logging.debug(
                "found existing well known file record for %s, updating", path
            )
            wkf.update(record)
            return

    logging.debug(
        "could not find existing well known file record for %s, appending",
        path,
    )
    wkfs.append(record)


def _connect(user="limsreader", host="limsdb2", database="lims2",
             password="limsro", port=5432):
    import pg8000

    conn = pg8000.connect(
        user=user, host=host, database=database, password=password, port=port
    )
    return conn, conn.cursor()


def _select(cursor, query):
    cursor.execute(query)
    columns = [
        d[0].decode("utf-8") if isinstance(d[0], bytes) else d[0]
        for d in cursor.description
    ]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def query(query, user="limsreader", host="limsdb2", database="lims2",
          password="limsro", port=5432):
    """Execute *query* against the LIMS PostgreSQL database and return rows."""
    conn, cursor = _connect(user, host, database, password, port)
    # Guard against non-ASCII characters
    query = "".join(c if ord(c) < 128 else " " for c in query)
    try:
        results = _select(cursor, query)
    finally:
        cursor.close()
        conn.close()
    return results


def safe_system_path(file_name):
    if platform.system() == "Windows":
        return linux_to_windows(file_name)
    else:
        return convert_from_titan_linux(os.path.normpath(file_name))


def convert_from_titan_linux(file_name):
    project_to_program = {
        "neuralcoding": "braintv",
        "0378": "celltypes",
        "conn": "celltypes",
        "ctyconn": "celltypes",
        "humancelltypes": "celltypes",
        "mousecelltypes": "celltypes",
        "shotconn": "celltypes",
        "synapticphys": "celltypes",
        "whbi": "celltypes",
        "wijem": "celltypes",
    }
    m = re.match(r"/projects/([^/]+)/vol1/(.*)", file_name)
    if m:
        return os.path.normpath(
            os.path.join(
                "/allen",
                "programs",
                project_to_program.get(m.group(1), "undefined"),
                "production",
                m.group(1),
                m.group(2),
            )
        )
    return file_name


def linux_to_windows(file_name):
    project_to_program = {
        "neuralcoding": "braintv",
        "0378": "celltypes",
        "conn": "celltypes",
        "ctyconn": "celltypes",
        "humancelltypes": "celltypes",
        "mousecelltypes": "celltypes",
        "shotconn": "celltypes",
        "synapticphys": "celltypes",
        "whbi": "celltypes",
        "wijem": "celltypes",
    }
    if re.match(r"/allen", file_name):
        return "\\" + file_name.replace("/", "\\")

    m = re.match(r"/data/([^/]+)/(.*)", file_name)
    if m:
        return os.path.normpath(
            os.path.join("\\\\aibsdata", m.group(1), m.group(2))
        )

    m = re.match(r"/projects/([^/]+)/vol1/(.*)", file_name)
    if m:
        return os.path.normpath(
            os.path.join(
                "\\\\allen",
                "programs",
                project_to_program.get(m.group(1), "undefined"),
                "production",
                m.group(1),
                m.group(2),
            )
        )
    return os.path.normpath(file_name)


def get_input_json(object_id, object_class, strategy_class, host="lims2",
                   **kwargs):
    query_string = (
        "http://{}/InputJsons?strategy_class={}&object_class={}&object_id={}"
    ).format(host, strategy_class, object_class, object_id)
    for key, value in kwargs.items():
        query_string += "&{}={}".format(key, value)
    return read_url_get(query_string)
