# Copyright 2015-2016 Allen Institute for Brain Science
# This file is part of Allen SDK.
#
# Allen SDK is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Allen SDK is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Allen SDK.  If not, see <http://www.gnu.org/licenses/>.


from morphology import *
from node import Node
from neuron_morphology.validation.result import InvalidMorphology
from neuron_morphology.validation.result import NodeValidationError


def read_swc(file_name, strict_validation=False):
    """  
    Read in an SWC file and return a Morphology object.

    Parameters
    ----------
    file_name: string
        SWC file name.
        
    strict_validation: boolean
        level of validation.

    Returns
    -------
    Morphology
        A Morphology instance.
    """
    nodes = []

    with open(file_name, "r") as f:
        for line in f:
            try:
                # remove comments
                if line.lstrip().startswith('#'):
                    continue
                # read values. expected SWC format is:
                #   ID, type, x, y, z, rad, parent
                # x, y, z and rad are floats. the others are ints
                toks = line.split()
                vals = Node(
                        n =  int(toks[0]),
                        t =  int(toks[1]),
                        x =  float(toks[2]),
                        y =  float(toks[3]),
                        z =  float(toks[4]),
                        r =  float(toks[5]),
                        pn = int(toks[6].rstrip())
                    )
                # store this node
                nodes.append(vals)
            except IndexError:
                message = "File is not recognized as a valid swc file. One of the columns is missing a value"
                raise InvalidMorphology([NodeValidationError(message, line[0], "Error")])

    return Morphology(node_list=nodes, strict_validation=strict_validation)
