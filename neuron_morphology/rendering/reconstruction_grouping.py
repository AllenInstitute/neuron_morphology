from collections import OrderedDict
from operator import itemgetter
from functools import cmp_to_key


class ReconstructionGrouping(object):

    def __init__(self, grouping, sub_groups, ungrouped_reconstructions):
        self._grouping = grouping
        self._sub_groups = sub_groups
        self._ungrouped_reconstructions = ungrouped_reconstructions

    @property
    def grouping(self):
        return self._grouping

    @property
    def sub_groups(self):
        return self._sub_groups

    @property
    def ungrouped_reconstructions(self):
        return self._ungrouped_reconstructions

    def __repr__(self):
        return "ReconstructionGrouping(%s, %s, %s)" % (self.grouping, self.sub_groups, self.ungrouped_reconstructions)


def create_reconstruction_grouping(reconstruction_hierarchy, reconstruction_sorting, reconstructions):

    if len(reconstruction_hierarchy) == 0:
        return ReconstructionGrouping(None, {}, sort_reconstructions(reconstruction_sorting, reconstructions))

    grouping = reconstruction_hierarchy[0]
    groups = {}
    ungrouped = []
    for reconstruction in reconstructions:
        attribute = grouping['attribute']
        if attribute not in reconstruction:
            ungrouped.append(reconstruction)
        else:
            group_name = reconstruction[attribute]
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(reconstruction)
    group_names = sorted(groups.keys(), reverse=grouping['sort'] == 'desc')
    sub_groups = OrderedDict()
    for group_name in group_names:
        sub_groups[group_name] = create_reconstruction_grouping(reconstruction_hierarchy[1:], reconstruction_sorting,
                                                                groups[group_name])
    ungrouped_reconstructions = sort_reconstructions(reconstruction_sorting, ungrouped)
    return ReconstructionGrouping(grouping, sub_groups, ungrouped_reconstructions)


def sort_reconstructions(reconstruction_sorting, reconstructions):

    comparers = []

    for item in reconstruction_sorting:
        comparers.append((itemgetter(item['attribute']), 1 if item['sort'] == 'asc' else -1))

    def comparer(left, right):
        for func, polarity in comparers:
            result = (func(left) > func(right)) - (func(left) < func(right))
            if result:
                return polarity * result
        return 0

    return sorted(reconstructions, key=cmp_to_key(comparer))
