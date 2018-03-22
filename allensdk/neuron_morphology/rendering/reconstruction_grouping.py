from collections import OrderedDict
from operator import itemgetter
from functools import cmp_to_key


class ReconstructionGrouping(object):

    """Class to group and sort reconstructions

    reconstructions are grouped and sorted in specified ascending and descending order.

    :parameter grouping: list of dicts
                top level grouping of reconstructions
    :parameter sub_groups: list of dicts
                nested grouping of reconstructions
    :parameter ungrouped_reconstructions: list of dicts
                list of reconstructions that are not grouped
    """

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

    """Creates groups of reconstruction and sorts them

    :parameter reconstruction_hierarchy: list of dicts
                categories to group the reconstructions by
    :parameter reconstruction_sorting: list of dicts
                categories to group the reconstructions by per row
    :parameter reconstructions: list of dicts
                list of reconstructions
    :return reconstruction_grouping: ReconstructionGrouping object
                nested groupings of reconstructions
    """

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
    reconstruction_grouping = ReconstructionGrouping(grouping, sub_groups, ungrouped_reconstructions)
    return reconstruction_grouping


def sort_reconstructions(reconstruction_sorting, reconstructions):

    """Sorts the reconstructions based on the criteria indicated by reconstruction_sorting

    :parameter reconstruction_sorting: list of dicts
                criteria for sorting the reconstructions by attribute and order
    :parameter reconstructions: list of dicts
                reconstructions that need to be sorted
    :return sorted_reconstructions: list
                list of reconstructions that are sorted
                [{'attribute1': '1', 'attribute2': '2'}, {'attribute1': '1', 'attribute2': '2'}
    """

    comparers = []

    for item in reconstruction_sorting:
        comparers.append((itemgetter(item['attribute']), 1 if item['sort'] == 'asc' else -1))

    def comparer(left, right):
        for func, polarity in comparers:
            result = (func(left) > func(right)) - (func(left) < func(right))
            if result:
                return polarity * result
        return 0

    sorted_reconstructions = sorted(reconstructions, key=cmp_to_key(comparer))
    return sorted_reconstructions
