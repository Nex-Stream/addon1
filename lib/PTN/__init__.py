#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://github.com/platelminto/parse-torrent-name
from .parse import PTN

__author__ = 'Giorgio Momigliano'
__email__ = 'gmomigliano@protonmail.com'
__version__ = '1.3'
__license__ = 'MIT'

ptn = PTN()


def parse(name):
    return ptn.parse(name)
