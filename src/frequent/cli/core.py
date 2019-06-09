#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Commands for the frequent CLI.
"""
#
#   Imports
#
from click import group
from click import pass_context
from click import style
from click import version_option

from ..__version__ import __version__
from .base import MainCLI
from .settings import CONTEXT_SETTINGS


#
#   Click commands
#

@group(cls=MainCLI, invoke_without_command=True,
       context_settings=CONTEXT_SETTINGS)
@pass_context
@version_option(prog_name=style('frequent', bold=True),
                version=__version__)
def cli(ctx):
    """
    Frequent CLI

      Frequently used components for Python projects.

    """
    pass


#
#   Entry-point
#

if __name__ == '__main__':
    cli()

