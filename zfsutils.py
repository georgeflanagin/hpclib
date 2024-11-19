# -*- coding: utf-8 -*-
"""
Functions to get information about ZFS datasets.
"""
import typing
from   typing import *

###
# Standard imports, starting with os and sys
###
min_py = (3, 11)
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

###
# Other standard distro imports
###

###
# Installed libraries like numpy, pandas, paramiko
###

###
# From hpclib
###
from   dorunrun import dorunrun
import linuxutils
from   urdecorators import trap

###
# imports and objects that were written for this project.
###

###
# Global objects
###

###
# Credits
###
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2024, University of Richmond'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = 'gflanagin@richmond.edu'
__status__ = 'in progress'
__license__ = 'MIT'


@trap
def get_dataset_info(dataset:str="") -> Union[dict, Generator[dict, None, None]]:
    """
    Retrieve disk usage for a dataset or datasets.

    dataset -- the name of the dataset. Empty string
        means all.

    returns -- a dict for one dataset, a generator expression
        if you are asking about all datasets.
    """
    if not dataset:
        return (get_dataset_info(dataset) for dataset in list_dataset())

    result = {}
    for line in dorunrun(f'zfs get -H used,reservation,available {dataset}',
                return_datatype=str).split('\n'):
        try:
            _0, key, value, _1 = line.split()
            result[key] = linuxutils.byte_size(value)
        except ValueError:
            pass

    return result


@trap
def get_pool_freespace(pool:str="") -> Union[dict,int]:
    """
    get the current freespace for any/all pools.

    pool -- name of a pool.

    returns -- an int if pool name is supplied, else returns
        dict keyed on pool names with ints as the values.
    """
    result = {}
    for line in dorunrun('zpool list -Hp -o name,free',
                    return_datatype=str).split('\n'):
        try:
            name, space = line.split()
            result[name] = int(space)
        except:
            pass

    return result if not pool else result.get(pool, -1)


@trap
def list_datasets(pool:str="") -> tuple:
    """
    find all the datasets in the current environment.

    pool -- name of the pool to search, or if this parameter
        is omitted, all pools.

    returns -- names of the datasets.
    """

    for line in dorunrun("zfs list -H -o name",
                    return_datatype=str).split('\n'):
        if line.startswith(pool):
            yield line


