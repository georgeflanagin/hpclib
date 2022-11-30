# -*- coding: utf-8 -*-
"""
Common constants to be used in recursive descent parsers.
"""
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

import datetime
import re
try:
    import parsec
except ImportError as e:
    print("This code requires parsec be installed.")
    sys.exit(os.EX_SOFTWARE)

###
# Credits
###
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2022'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = ['me@georgeflanagin.com', 'gflanagin@richmond.edu']
__status__ = 'in progress'
__license__ = 'MIT'


###
# Constants
###
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
SEMICOLON   = ';'
BACKSLASH   = '\\'
UNDERSCORE  = '_'
OCTOTHORPE  = '#'
CIRCUMFLEX  = '^'
EMPTY_STR   = ""


SLASH   = '/'
PLUS    = '+'
MINUS   = '-'
STAR    = '*'    
EQUAL   = '='
DOLLAR  = '$'
AT_SIGN = '@'
BANG    = '!'
PERCENT = '%'

###
# Regular expressions.
###
# Either "0" or something that starts with a non-zero digit, and may
# have other digits following.
DIGIT_STR   = parsec.regex(r'(0|[1-9][\d]*)')

# Spec for how a floating point number is written.
IEEE754     = parsec.regex(r'-?(0|[1-9][\d]*)([.][\d]+)?([eE][+-]?[\d]+)?')

# IP address
IPv4_ADDR   = parsec.regex(r'(?:(?:25[0-5]|2[0-4][\d]|[01]?[\d][\d]?)\.){3}(?:25[0-5]|2[0-4][\d]|[01]?[\d][\d]?)')

# Something Python thinks is an integer.
PYINT       = parsec.regex(r'[-+]?[\d]+')

# HH:MM:SS in 24 hour format.
TIME            = parsec.regex(r'(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d)')

# ISO Timestamp
TIMESTAMP   = parsec.regex(r'[\d]{1,4}/[\d]{1,2}/[\d]{1,2} [\d]{1,2}:[\d]{1,2}:[\d]{1,2}')

# US 10 digit phone number, w/ or w/o dashes and spaces embedded.
US_PHONE    = parsec.regex(r'[2-9][\d]{2}[ -]?[\d]{3}[ -]?[\d]{4}')

# A lot of nothing.
WHITESPACE  = parsec.regex(r'\s*', re.MULTILINE)

###
# trivial parsers.
###
lexeme          = lambda p: p << WHITESPACE
minus           = lexeme(parsec.string(MINUS))
positive_number = lexeme(DIGIT_STR).parsecmap(int) 
negative_number = lexeme(minus >> positive_number).parsecmap(lambda x: -x)
quote           = parsec.string(QUOTE2)

###
# Functions for parsing more complex elements.
###
def integer() -> int:
    """
    Return a Python int, based on the commonsense def of a integer.
    """
    return lexeme(PYINT).parsecmap(int)


def number() -> float:
    """
    Return a Python float, based on the IEEE754 character representation.
    """
    return lexeme(IEEE754).parsecmap(float)


def time() -> datetime.time:
    """
    For 24 hour times.
    """
    return lexeme(TIME).parsecmap(datetime.time)


def timestamp() -> datetime.datetime:
    """
    Convert an ISO timestamp to a datetime.
    """
    return lexeme(TIMESTAMP).parsecmap(datetime.datetime.fromisoformat)


def charseq() -> str:
    """
    Returns a sequence of characters, resolving any escaped chars.
    """
    def string_part():
        return parsec.regex(r'[^"\\]+')

    def string_esc():
        global TAB, CR, LF, VTAB, BSPACE
        return parsec.string(BACKSLASH) >> (
            parsec.string(BACKSLASH)
            | parsec.string('/')
            | parsec.string('b').result(BSPACE)
            | parsec.string('f').result(VTAB)
            | parsec.string('n').result(LF)
            | parsec.string('r').result(CR)
            | parsec.string('t').result(TAB)
            | parsec.regex(r'u[0-9a-fA-F]{4}').parsecmap(lambda s: chr(int(s[1:], 16)))
            | quote
        )
    return string_part() | string_esc()


@lexeme
@parsec.generate
def quoted() -> str:
    yield quote
    body = yield parsec.many(charseq())
    yield quote
    raise EndOfGenerator(''.join(body))


class EndOfParse(StopIteration):
    """
    An exception raised when parsing operations terminate. Iterators raise
    a StopIteration exception when they exhaust the input; this mod gives
    us something useful back.
    """
    def __init__(self, value):
        self.value = value

