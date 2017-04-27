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
        self.file_record = dict()

    def add_swc_errors(self, swc_file, errors):
        """ This function creates a report for swc validation """

        record = OrderedDict()
        record["file_name"] = swc_file
        record["errors"] = []

        for error in errors:
            error_record = OrderedDict()
            error_record['message'] = error.message
            error_record['ids'] = error.node_ids
            error_record['severity'] = error.severity
            record["errors"].append(error_record)

        self.file_record[swc_file] = record

    def add_marker_errors(self, marker_file, errors):

        """ This function creates a report for a marker validation """
        record = OrderedDict()
        record['file_name'] = marker_file
        record['errors'] = []

        spacing = [.1144, .1144, .28]

        for error in errors:
            error_record = OrderedDict()
            error_record['message'] = error.message

            error.marker['x'] += spacing[0]
            error.marker['y'] += spacing[1]
            error.marker['z'] += spacing[2]

            error_record['marker'] = error.marker
            error_record['severity'] = error.severity
            record["errors"].append(error_record)

        self.file_record[marker_file] = record

    def to_json(self):
        return json.dumps(self.file_record.values(), indent=4, separators=(',', ': '))
