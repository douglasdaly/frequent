# -*- coding: utf-8 -*-
"""
Documentation related tasks.
"""
from glob import glob
import os
import re

import invoke

from .helpers import log as hlog


#
#   Helpers
#

def log(msg, level=None):
    return hlog(msg, name='docs', level=level)


#
#   Tasks
#

@invoke.task
def generate_make(ctx):
    """Generates the documentation for the project's Makefile"""
    file = os.path.join('docs', 'development', 'makefile_help.txt')

    log('Generating help file')
    ctx.run("make help > %s" % file)
    with open(file, 'r') as fin:
        contents = fin.readlines()

    log('Replacing color codes')
    pattern = re.compile(r'\x1b\[\d+m')
    output = list()
    for line in contents[1:-1]:
        output.append(pattern.sub('', line))

    log('Saving new file')
    with open(file, 'w') as fout:
        fout.writelines(output)

    return


@invoke.task
def clean_apidocs(ctx):
    """Cleans the auto-generated API documentation files"""
    log('Cleaning API documentation')
    for f in glob(os.path.join('docs', 'api', '*.rst')):
        if f in ('modules.rst', 'frequent.rst'):
            continue
        os.remove(f)
    return

