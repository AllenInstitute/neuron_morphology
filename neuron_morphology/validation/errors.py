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


class ValidationError(object):

    def __init__(self, message, node_id, is_fatal):
        self._message = message
        self._node_id = node_id
        self._is_fatal = is_fatal

    @property
    def message(self):
        return self._message

    @property
    def node_id(self):
        return self._node_id

    @property
    def is_fatal(self):
        return self._is_fatal

    def __repr__(self):
        return "Message: %s, Node ID: %s, Fatal: %s" % (self._message, self._node_id, self._is_fatal)


class InvalidMorphology(ValueError):

    def __init__(self, validation_errors):
        ValueError.__init__(self, "Morphology appears to be inconsistent")
        self._validation_errors = validation_errors

    @property
    def validation_errors(self):
        return self._validation_errors

    def __str__(self):
        return "%s, Errors: %s" % (ValueError.__str__(self), self._validation_errors.__str__())