#! /usr/bin/env python3
"""
"""


# from __future__ import


__all__ = [
    'ENVIRONMENT',
    'REQUEST_ATTRS',
    'REQUEST_LOG',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>"
]


import os


ENVIRONMENT = os.environ.get('ENVIRONMENT', 'local')
REQUEST_ATTRS = ('_request_id', '_started_at')
REQUEST_LOG = (
    '{request_id}: '
    + '{url} '
    + '{method} '
    + '{status} '
    + 'time: (delta_time: {delta}[{t_unit}]), '
    + 'size: ({size}[{s_unit}]) '
    + '{reason}'
)
