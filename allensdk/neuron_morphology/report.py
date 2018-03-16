# Copyright 2015-2017 Allen Institute for Brain Science
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
# Author: Nika Keller

import json
from collections import OrderedDict


class Report(object):

    def __init__(self):
        self.file_record = OrderedDict()
        self.stat_file_record = dict()

    def add_swc_results(self, swc_file, results):

        record = OrderedDict()
        record["file_name"] = swc_file
        record["results"] = []

        for result in results:
            result_record = OrderedDict()
            result_record['message'] = result.message
            result_record['ids'] = result.node_ids
            result_record['level'] = result.level
            record["results"].append(result_record)

        self.file_record[swc_file] = record

    def add_marker_results(self, marker_file, results):

        record = OrderedDict()
        record['file_name'] = marker_file
        record['results'] = []

        for result in results:
            result_record = OrderedDict()
            result_record['message'] = result.message
            result_record['marker'] = result.marker
            result_record['level'] = result.level
            record["results"].append(result_record)

        self.file_record[marker_file] = record

    def add_swc_stats(self, swc_file, stats):

        """ This function creates a report for swc statistics """

        record = self.file_record[swc_file]
        if not record:
            record = OrderedDict()
            record['file_name'] = swc_file
        record['stats'] = stats

        self.file_record[swc_file] = record

    def to_json(self):
        return json.dumps(self.file_record.values(), indent=4, separators=(',', ': '))

    def has_results(self):

        for record in self.file_record.values():
            if record["results"]:
                return True
        else:
            return False
