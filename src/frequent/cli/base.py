# -*- coding: utf-8 -*-
"""
Base objects for the CLI interface.
"""
#
#   Imports
#
from click import Group

from .utils import is_truthy


#
#   Click customizations
#

class MainCLI(Group):
    """
    Customized click group class for CLI
    """

    def parse_args(self, ctx, args):
        ctx.meta['develop'] = self._set_develop(ctx, args)
        return super().parse_args(ctx, args)

    def _set_develop(self, ctx, args):
        """Determine if we're in develop mode or not"""
        if 'develop' in ctx.meta:
            return ctx.meta['develop']
        if '--develop' in args:
            return True
        if is_truthy('FREQUENT_DEVELOP'):
            return True
        return False

