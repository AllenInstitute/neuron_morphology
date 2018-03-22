# Copyright 2016 Allen Institute for Brain Science
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
import node

class Segment(object):
    """ Represents the series of nodes existing between two branching
        points, or branching point and tip
    """

    def __init__(self):
        pass
        self.node_list = []
        self.path_length = 0
        self.max_euclidean_distance = 0
        self.euclidean_distance = 0
        self.branch_order = -1

    def add_node(self, n):
        self.node_list.append(n)

    def _reorder_node_list(self, morph):
        """ Internal procedure
            Reorder node list so that root is at head of list and
            nodes are stored sequentially (ie, where child is after
            parent)
        """
        # if there are no elements then there's nothing to do
        if len(self.node_list) == 0:
            return
        # perform consistency check to make sure segment is connected
        #   and that no nodes have children, except possibly the tip
        # reorder to put the segment in sequential order, with segment
        #   root as the first list element
        child_map = {}      # map of node to children
        parent_map = {}     # map of node to parent
        for n in self.node_list:
            if len(n.children) > 1 or len(n.children) == 0:
                child = None  # must be segment tip
                segment_tip = n
            else:
                child = morph.node(n.children[0])
            child_map[n] = child
            if n.parent < 0:
                par = None  # must be segment root
                segment_root = n
            else:
                par = morph.node(n.parent)
                if par.t == 1 or len(par.children) > 1:
                    par = None  # must be segment root
                    segment_root = n
                else:
                    par = morph.node(n.parent)
            parent_map[n] = par
        # make sure there's only one root and only one tip
        tips = 0
        for k,v in child_map.iteritems():
            if v is None:
                tips += 1
        roots = 0
        for k,v in parent_map.iteritems():
            if v is None:
                roots += 1
        err = ""
        if tips != 1:
            if tips == 0:
                err += "Segment is not properly terminated.\n"
            else:
                err += "Segment has more than one tip.\n"
            err += "Segment must terminate with neurite tip or bifurcation point\n"
        if roots != 1:
            if len(err) > 0:    # add spacer before reporting next error
                err += "----------"
            if roots == 0:
                err += "Segment has no root (is it circular?)."
            else:
                err += "Segment has multiple roots."
        if len(err) > 0:
            raise Exception(err)
        # re-order list
        orig = self.node_list
        self.node_list = []
        self.node_list.append(segment_root)
        while segment_root != segment_tip:
            segment_root = child_map[segment_root]
            self.node_list.append(segment_root)
        for i in range(len(self.node_list)):
            n = self.node_list[i]
            #n.segment = self   -- this is done in Morphology
            n.segment_id = i
            n.segment_pid = i-1
            
    def _calculate_path_length(self):
        """ Internal function to calculate the path length of the segment
        """
        self.path_length = 0.0
        if len(self.node_list) < 2:
            return
        parent = self.node_list[0]
        for i in range(1, len(self.node_list)):
            child = self.node_list[i]
            self.path_length += node.euclidean_distance(parent, child)
            parent = child
            
    def _calculate_euclidean_distance(self):
        """ Internal function to calculate euclidean distance between
            segment root and tip, and also the maximum distance
            from the segment root to any part of the segment
        """
        self.euclidean_distance = 0.0
        self.max_euclidean_distance = 0.0
        if len(self.node_list) < 2:
            return
        root = self.node_list[0]
        max_dist = 0
        for i in range(1, len(self.node_list)):
            n = self.node_list[i]
            dist = node.euclidean_distance(root, n)
            if dist > max_dist:
                max_dist = dist
        self.max_euclidean_distance = max_dist
        # when we get here, n is the last entry in the node list
        self.euclidean_distance = node.euclidean_distance(root, n)
            
        
    def setup(self, morph):
        """ Once all nodes are added, this function calculates the
            path length and the maximum euclidean distance from
            the segment root.
        """
        self._reorder_node_list(morph)
        self._calculate_path_length()
        self._calculate_euclidean_distance()
        

    def set_branch_order(self, order):
        self.branch_order = order

    
    def __str__(self):
        desc = "%d nodes\n" % len(self.node_list)
        desc += "Start: " + str(self.node_list[0]) + "\n"
        desc += "End: " + str(self.node_list[-1]) + "\n"
        a = self.path_length
        b = self.euclidean_distance
        c = self.max_euclidean_distance
        d = self.branch_order
        desc += "Path: %f, Euclidean: %f (%f), Order=%d" % (a, b, c, d)
        return desc

