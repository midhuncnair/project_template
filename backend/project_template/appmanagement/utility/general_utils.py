"""
This general utils module for appManagement
"""

# from __future__ import


__all__ = [
    'sort_migration_files',
    'gather_migration_files',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


import os
import logging

from django.apps import apps


logger = logging.getLogger(__name__)


def sort_migration_files(item):
    item_split = item.split('_')
    start = item_split[0]
    try:
        start = int(start)
    except:
        return 0
    else:
        return start


def gather_migration_files():
    """Gathers the current set of migration files from all listed apps
    returns both the sorted list and the latest.
    """
    app_configs = apps.app_configs
    ret_item = {}
    for app_config in app_configs:
        mig = os.path.join(app_configs[app_config].path, 'migrations')
        dir_list = []
        try:
            dir_list = os.listdir(mig)
        except FileNotFoundError:
            continue
        dir_list = [
            item
            for item in dir_list
            if (
                os.path.isfile(os.path.join(mig, item))
                and item.endswith('.py')
                and item != '__init__.py'
            )
        ]

        dir_list.sort(
            key=sort_migration_files
        )

        ret_item[app_config] = {
            'files': dir_list,
            'latest': dir_list[-1],
        }
    return ret_item
