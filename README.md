# Frequent

*Frequently used components for Python projects.*


[![PyPI Version](https://img.shields.io/pypi/v/frequent.svg)](https://pypi.org/project/frequent/ "PyPI Page")
[![Build Status](https://travis-ci.org/douglasdaly/frequent-py.svg?branch=master)](https://travis-ci.org/douglasdaly/frequent-py "Travis CI")
[![Coverage Status](https://coveralls.io/repos/github/douglasdaly/frequent-py/badge.svg)](https://coveralls.io/github/douglasdaly/frequent-py "Coveralls")
[![Documentation Status](https://readthedocs.org/projects/frequent-py/badge/?version=latest)](https://frequent-py.readthedocs.io/en/latest/?badge=latest "Documentation")
[![Python Versions](https://img.shields.io/pypi/pyversions/frequent.svg)](https://pypi.org/project/frequent "PyPI Page")

- Free software: [MIT License](./LICENSE "License File")
- Documentation: https://frequent-py.readthedocs.io/


## Installation

You have a few options for installing/using `frequent`.  The first is to
install using your package manager of choice, `pipenv` for instance:

```bash
$ pipenv install frequent
```

However, taking a cue from the excellent 
[boltons](https://github.com/mahmoud/boltons "boltons on Github") 
package, each component is self-contained in its respective file/folder
allowing for easy vendorization.  Components are not dependent on one
another and rely solely on the standard library.  This makes
vendorization of a component as simple as copying just the file/folder
for the component(s) that you need (same goes for the unit tests).


## About

I found myself copying/re-writing certain components for my projects
over and over again.  This library is an attempt to take some of the
components I find myself needing frequently and package them up in a
convenient and easy-to-use manner.

### Features

- ``config``: for global configuration/settings management.
- ``messaging``: components for creating custom messaging frameworks.
- ``singleton``: for singleton classes.


## License

Frequent &copy; Copyright 2019, Douglas Daly.  All rights reserved. This
project is licensed under the MIT License, see the 
[`LICENSE`](./LICENSE "License File") file for more details.

