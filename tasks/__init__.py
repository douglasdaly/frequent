# -*- coding: utf-8 -*-
"""
Invoke commands for common tasks.
"""
#
#   Imports
#
import dotenv
import invoke

from . import develop
from . import docs
from . import generate
from . import release

dotenv.load_dotenv()

namespace = invoke.Collection(develop, docs, generate, release)
