# Vendored from allensdk.core.json_utilities (AllenInstitute/AllenSDK).
# Original: Allen Institute Software License (2-clause BSD + non-commercial clause).
# Copyright 2015-2016. Allen Institute. All rights reserved.
#
# Modifications: removed allensdk dependency; made simplejson optional
# (falls back to stdlib json for basic read/write operations).

import logging
import re

import numpy as np

try:
    import simplejson as json
    _SIMPLEJSON = True
except ImportError:
    import json
    _SIMPLEJSON = False

try:
    import urllib.request as urllib_request
    from urllib.parse import urlparse, urlunsplit, parse_qsl
except ImportError:
    import urllib2 as urllib_request
    from urlparse import urlparse, urlunsplit, parse_qsl

ju_logger = logging.getLogger(__name__)


def read(file_name):
    """Read JSON from a file and return the parsed object."""
    with open(file_name, "rb") as f:
        json_string = f.read().decode("utf-8")
        if len(json_string) == 0:
            json_string = "{}"
        return json.loads(json_string)


def write(file_name, obj):
    """Write *obj* as JSON to *file_name*, handling numpy types."""
    with open(file_name, "wb") as f:
        s = write_string(obj)
        try:
            f.write(s)          # Python 2
        except TypeError:
            f.write(s.encode("utf-8"))  # Python 3


def write_string(obj):
    """Serialize *obj* to a JSON string, handling numpy types."""
    kwargs = dict(indent=2, default=json_handler)
    if _SIMPLEJSON:
        kwargs.update(ignore_nan=True, iterable_as_array=True)
    return json.dumps(obj, **kwargs)


def read_url(url, method="POST"):
    if method == "GET":
        return read_url_get(url)
    elif method == "POST":
        return read_url_post(url)
    else:
        raise ValueError("Unknown request method: %s" % method)


def read_url_get(url):
    """Fetch JSON from *url* via GET and return the parsed object."""
    response = urllib_request.urlopen(url)
    return json.loads(response.read().decode("utf-8"))


def read_url_post(url):
    """Fetch JSON from *url* via POST and return the parsed object."""
    urlp = urlparse(url)
    main_url = urlunsplit((urlp.scheme, urlp.netloc, urlp.path, "", ""))
    data = json.dumps(dict(parse_qsl(urlp.query)))

    opener = urllib_request.build_opener(urllib_request.HTTPHandler())
    request = urllib_request.Request(main_url, data)
    request.add_header("Content-Type", "application/json")
    request.get_method = lambda: "POST"

    try:
        response = opener.open(request)
    except Exception as e:
        response = e

    return json.loads(response.read())


def json_handler(obj):
    """Custom JSON serializer for types not handled by the stdlib encoder."""
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    elif hasattr(obj, "isoformat"):
        return obj.isoformat()
    else:
        raise TypeError(
            "Object of type %s with value %s is not JSON serializable"
            % (type(obj), repr(obj))
        )


class JsonComments(object):
    """Read JSON files that contain JavaScript-style ``//`` or ``/* */`` comments."""

    _oneline_comment = re.compile(r"\/\/.*$", re.MULTILINE)
    _multiline_comment_start = re.compile(r"\/\*", re.MULTILINE | re.DOTALL)
    _multiline_comment_end = re.compile(r"\*\/", re.MULTILINE | re.DOTALL)
    _blank_line = re.compile(r"\n?^\s*$", re.MULTILINE)
    _carriage_return = re.compile(r"\r$", re.MULTILINE)

    @classmethod
    def read_string(cls, json_string):
        return json.loads(cls.remove_comments(json_string))

    @classmethod
    def read_file(cls, file_name):
        try:
            with open(file_name) as f:
                return cls.read_string(f.read())
        except ValueError:
            ju_logger.error(
                "Could not load json object from file: %s", file_name
            )
            raise

    @classmethod
    def remove_comments(cls, json_string):
        """Strip ``//`` and ``/* */`` comments from a JSON string."""
        json_string = cls._oneline_comment.sub("", json_string)
        json_string = cls._carriage_return.sub("", json_string)
        json_string = cls.remove_multiline_comments(json_string)
        json_string = cls._blank_line.sub("", json_string)
        return json_string

    @classmethod
    def remove_multiline_comments(cls, json_string):
        new_json = []
        start_iter = cls._multiline_comment_start.finditer(json_string)
        slice_start = 0
        for comment_start in start_iter:
            new_json.append(json_string[slice_start:comment_start.start()])
            search_start = comment_start.end()
            comment_end = cls._multiline_comment_end.search(
                json_string[search_start:]
            )
            if comment_end is None:
                break
            slice_start = search_start + comment_end.end()
        new_json.append(json_string[slice_start:])
        return "".join(new_json)
