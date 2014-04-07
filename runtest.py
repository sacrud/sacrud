#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Test runner
"""
# nosetests --cover-package=sacrud --cover-erase --with-coverage  --with-doctest
import sys

import coverage
import nose

# --with-doctest
argv = sys.argv[:]
argv.insert(1, "--cover-package=sacrud")
argv.insert(2, "--cover-erase")
argv.insert(3, "--with-coverage")
argv.insert(4, "--with-doctest")
nose.main(argv=argv)
result = nose.run()
