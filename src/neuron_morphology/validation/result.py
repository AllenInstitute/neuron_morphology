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


class NodeValidationError(object):

    def __init__(self, message, node_ids, level):
        self._message = message
        if type(node_ids) is list:
            self._node_ids = node_ids
        else:
            self._node_ids = [node_ids]
        self._level = level

    @property
    def message(self):
        return self._message

    @property
    def node_ids(self):
        return self._node_ids

    @property
    def level(self):
        return self._level

    def __repr__(self):
        return "Message: %s, Node ID: %s, Level: %s" % (self._message, self._node_ids, self.level)


class MarkerValidationError(object):

    def __init__(self, message, marker, level):
        self._message = message
        if type(marker) is list:
            self._marker = marker
        else:
            self._marker = [marker]
        self._level = level

    @property
    def message(self):
        return self._message

    @property
    def marker(self):
        return self._marker

    @property
    def level(self):
        return self._level

    def __repr__(self):
        return "Message: %s, Marker: %s, Level: %s" % (self._message, self._marker, self._level)


class InvalidMorphology(ValueError):

    def __init__(self, validation_errors):
        super(InvalidMorphology, self).__init__("Morphology appears to be inconsistent")
        self._validation_errors = validation_errors

    @property
    def validation_errors(self):
        return self._validation_errors

    def __str__(self):
        return "%s, Errors: %s" % (ValueError.__str__(self), self._validation_errors.__str__())


class InvalidMarkerFile(ValueError):

    def __init__(self, validation_errors):
        super(InvalidMarkerFile, self).__init__("Marker file is not valid")
        self._validation_errors = validation_errors

    @property
    def validation_errors(self):
        return self._validation_errors

    def __str__(self):
        return "%s, Errors: %s" % (ValueError.__str__(self), self._validation_errors.__str__())
