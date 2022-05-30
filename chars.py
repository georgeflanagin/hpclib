# -*- coding: utf-8 -*-
import typing
from   typing import *

min_py = (3, 8)

###
# Standard imports, starting with os and sys
###
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

###
# Credits
###
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2022'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = ['gflanagin@richmond.edu', 'me@georgeflanagin.com']
__status__ = 'in progress'
__license__ = 'MIT'

import enum

class Char(enum.Enum):
    TAB     = '\t'
    CR      = '\r'
    LF      = '\n'
    VTAB    = '\f'
    BSPACE  = '\b'
    QUOTE1  = "'"
    QUOTE2  = '"'
    QUOTE3  = "`"
    LBRACE  = '{'
    RBRACE  = '}'
    LBRACK  = '['
    RBRACK  = ']'
    COLON   = ':'
    COMMA   = ','
    BACKSLASH   = '\\'
    UNDERSCORE  = '_'
    OCTOTHORPE  = '#'
    EMPTY_STR   = ""
    EQUAL = '='
    DASH = '-'

