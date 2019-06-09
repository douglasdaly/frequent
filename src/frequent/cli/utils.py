# -*- coding: utf-8 -*-
"""
Utilities for the CLI interface.
"""
#
#   Imports
#
import os


#
#   Utility functions
#

def is_truthy(name):
    """Gets whether or not the  given environment variable is 'truthy'

    Parameters
    ----------
    name : str
        Name of the environment variable to check for truthiness.

    Returns
    -------
    bool
        Whether or not the given `name` is true or not.

    """
    ret = os.getenv(name)
    if ret is not None:
        try:
            ret = int(ret[0])
        except ValueError:
            pass
        if isinstance(ret, str):
            ret = ret.lower()
            if ret not in ('f', 'false'):
                return True
            return False
        elif isinstance(ret, int):
            return ret > 0
        return True
    return False

