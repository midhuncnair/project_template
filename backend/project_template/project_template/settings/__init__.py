#! /usr/bin/env python3
"""
"""


import os


ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')


print("The environment is %s" % ENVIRONMENT)


if ENVIRONMENT == 'local':
    from .local import *
elif ENVIRONMENT == 'development':
    from .dev import *
elif ENVIRONMENT == 'staging':
    from .dev import *
else:
    from .prod import *


SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY

print("The installed_apps = ", INSTALLED_APPS)