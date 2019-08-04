# -*- coding: utf-8 -*-
"""
Tasks related to releases.
"""
from .helpers import log as hlog


#
#   Helpers
#

def log(msg, level=None):
    hlog(msg, name='release', level=level)
