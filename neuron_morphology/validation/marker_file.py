import sys

def validate_marker(fname):
    print("Evaluating '%s'" % fname)
    err = False
    # make sure the name contains 'marker'
    if len(fname.split('marker')) == 1:
        print("ERROR: File name does not contain string 'marker'.")
        err = True
    # make sure there are an appropriate number of columns
    with open(fname, "r") as f:
        cnt = 0
        line_err = False
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            cnt += 1
            if line[0] == '#':
                continue
            cols = line.split(',')
            if len(cols) != 10 and not line_err:
                print("ERROR: Line %d has %d CSV column(s). Expected 10." % (cnt, len(cols)))
                err = True
                line_err = True
    if not err:
        print("OK")
    # TODO consider looking for a node for each marker point in the associated
    #   SWC file
    return err

#validate_marker("Ntsr1-Cre_Ai14-214922.03.02.01_508278663_marker_m.swc")
#validate_marker("Ntsr1-Cre_Ai14-214922.03.02.01_508278663_marker.swc")
#validate_marker("Cux2-CreERT2_Ai14-207760.03.01.01_496163976_marker_m.swc")
#validate_marker("Cux2-CreERT2_Ai14-207760.03.01.01_496163976_marker.swc")

#if len(sys.argv) != 2:
#    print("Usage: %s <marker file>" % sys.argv[0])
#    sys.exit(1)

#if validate_marker(sys.argv[1]):
#    sys.exit(1)