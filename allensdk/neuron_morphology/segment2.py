class Segment2(object):
    """ Represents the series of nodes existing between two branching
        points, or branching point and tip
    """

    def __init__(self):
        pass
        self.node_list = []

    def add_node(self, node):
        self.node_list.append(node)
