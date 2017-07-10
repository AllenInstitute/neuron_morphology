#!/usr/bin/python
import numpy as np
import sys
sys.path.append("/home/keithg/allen/neuron_morphology/")
import os.path
import math
import psycopg2
import psycopg2.extras
import prep_upright
import neuron_morphology.swc as swc
import neuron_morphology.visualization.morphvis as morphvis

#spec_ids = [488677994]
spec_ids = [569072334]
#spec_ids = [486896849, 475057898, 473543792, 488677994]

########################################################################
# database interface 
#
# connect to database
try:
  conn_string = "host='limsdb2' dbname='lims2' user='atlasreader' password='atlasro'"
  conn = psycopg2.connect(conn_string)
  cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
except:
  print "unable to connect to database"
  raise

# fetch SWC file for specimen ID
name_sql = ""
name_sql += "SELECT spec.id, spec.name, wkf.filename, wkf.storage_directory \n"
name_sql += "FROM specimens spec \n"
name_sql += "JOIN neuron_reconstructions nr ON nr.specimen_id=spec.id \n"
name_sql += "  AND nr.superseded = 'f' AND nr.manual = 't' \n"
name_sql += "JOIN well_known_files wkf ON wkf.attachable_id=nr.id \n"
name_sql += "  AND wkf.attachable_type = 'NeuronReconstruction' \n"
name_sql += "JOIN cell_soma_locations csl ON csl.specimen_id=spec.id \n"
name_sql += "JOIN well_known_file_types wkft \n"
name_sql += "  ON wkft.id=wkf.well_known_file_type_id \n"
name_sql += "WHERE spec.id=%d AND wkft.name = '3DNeuronReconstruction'; \n"

def fetch_specimen_record(spec_id):
    global cursor
    cursor.execute(name_sql % spec_id)
    result = cursor.fetchall()
    spec_id = -1
    spec_name = ""
    name = ""
    path = ""
    record = {}
    if len(result) > 0:
        record["spec_id"] = result[0][0]
        record["spec_name"] = result[0][1]
        record["filename"] = result[0][2]
        record["path"] = result[0][3]
    return record

# make upright versions of each morphology
for spec_id in spec_ids:
    dname = "%d" % spec_id
    if not os.path.isdir(dname):
        os.makedirs(dname)
    fname = "%s/%d.swc" % (dname, spec_id)
    if not os.path.isfile(fname):
        record = fetch_specimen_record(spec_id)
        # calculate upright transform
        aff = prep_upright.calculate_transform(cursor, spec_id)
        # open SWC file and apply upright transform
        nrn = swc.read_swc(record["path"] + record["filename"])
        nrn.apply_affine(aff)
        # save morphology
        nrn.save("%d.swc" % spec_id)


########################################################################
# make thumnails for each image frame and store these in a directory
#   with the same name as the specimen ID

# frame size in pixels
width = 800
height = 800

# movie is on a black background, while the soma is normally black
# change soma color so it is visible
mc = morphvis.MorphologyColors()
mc.soma = mc.basal
#mc.soma = (224, 224, 0)

# for each specimen ID, create series of image frames
for spec_id in spec_ids:
    nrn = swc.read_swc("%d.swc" % spec_id)
    # per Staci and Nathan, correct for shrinkage along Z axis
    # use approximate value of 67% shrinkage
    for n in nrn.node_list:
        n.z = n.z * 3.0
    scale_factor, scale_inset_x, scale_inset_y = morphvis.calculate_scale(nrn, width, height)
    #############
    # HACK ALERT
    # if a cell is not centered and auto-scaling makes it rotate outside
    #   the frame area, adjust its scale plus x/y inset value -- adjust
    #   these until rotation is as desired
    if scale_factor > 1.25:
        scale_factor = 1.25
        scale_inset_x += 125 
    # /HACK ALERT
    #############
    ctr = 0
    clone = nrn.clone()
    for i in range(0, 360):
        # make clone of morphology and rotate it by i degrees
        clone.rotate(1.0)
        # create thumbnail image with black background
        # create canvas
        thumb = morphvis.create_image(width, height, alpha=True, color=(0, 0, 0, 255))
        # draw on canvas
        morphvis.draw_morphology_2(thumb, clone, scale_factor=scale_factor, inset_left=scale_inset_x, inset_top=scale_inset_y, colors=mc)
        # write file
        fname = "%d/img%04d.png" % (spec_id, ctr)
        ctr += 1
        print("Writing '%s'" % fname)
        thumb.save(fname)
        
# to generate movie, use e.g.,
#   ffmpeg -i 488677994/img%04d.png -q:v 5 name.compress5.mpg
# compression (quality) levels should range from 1 (best quality) 
#   to 31 (best compression)

