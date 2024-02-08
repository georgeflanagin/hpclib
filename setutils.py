# -*- coding: utf-8 -*-
""" Generic, bare functions, not a part of any object or service. """

# Added for Python 3.5+
import typing
from typing import *

import os
import sys

# Credits
__longname__ = "University of Richmond"
__acronym__ = " UR "
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2015, University of Richmond'
__credits__ = None
__version__ = '0.1'
__maintainer__ = 'George Flanagin'
__email__ = 'gflanagin@richmond.edu'
__status__ = 'Prototype'

__license__ = 'MIT'

PHI=frozenset()

# Cheap hack so that "*" means "every{minute|hour|etc}"
class Universal(set):
    """
    Universal set - match everything. No matter the value
    of item, s.o.b., Mr. Wizard, it's there!
    """
    def __contains__(self, item): return True

star = Universal() 

def notlikeanyof(search_term:str, sock_drawer:Iterable) -> bool:
    """ 
    Look for something in the sock_drawer that is like the sock you have. 
    """
    try:
        return not any(_sock in search_term for _sock in sock_drawer)
    except TypeError as e:
        tombstone(f"{sock_drawer} is of type {type(sock_drawer)}, and not iterable.")
        raise NotImplementedError from None


def nothinglikeit(search_term:str, sock_drawer:Iterable) -> bool:
    """ 
    A crude implementation of "not any". This function decides if your sock
    is sorta-like any of the socks.  
    """
    try:
        return not any(_sock.startswith(search_term) for _sock in sock_drawer)
    except TypeError as e:
        tombstone(f"{sock_drawer} is of type {type(sock_drawer)}, and not iterable.")
        raise NotImplementedError from None


def set_encoder(obj:Any) -> str:
    """
    The python set type is not serializable in JSON. Convert it to 
    list first.

    If the argument is /not/ a set type, then we pass it along
    to the bog standard encoder.
    """
    if isinstance(obj, set):
        return [ _ for _ in obj ]
    return obj


def setify(obj):
    """
    If it is not a set going in, it will be coming out.
    """
    global star
    if str(obj) == '*':
        return star
    if isinstance(obj, int):
        return set([obj])  # Single item
    if isinstance(obj, list) and obj[0] == '*':
        return star
    if not isinstance(obj, set):
        obj = set(obj)
    return obj

