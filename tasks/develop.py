# -*- coding: utf-8 -*-
"""
Tasks related to project development.
"""
#
#   Imports
#
import glob

import invoke

from .helpers import log as hlog


#
#   Helpers
#

def log(msg, level=None):
    hlog(msg, name='develop', level=level)


#
#   Script functions
#

@invoke.task
def update_requirements(ctx):
    """Updates the requirements.txt files"""
    for r_file in glob.glob('./requirements*.txt'):
        log('Processing %s' % r_file)
        with open(r_file, 'r') as fin:
            contents = fin.readlines()
        out = []
        for ln in contents:
            ln = ln.strip()
            if '-e .' in ln and '--no-use-pep517' not in ln:
                ln = '%s %s' % ('--no-use-pep517', ln)
            out.append(ln)
        with open(r_file, 'w') as fout:
            fout.write('\n'.join(out))
    return

