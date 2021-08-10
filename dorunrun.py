# -*- coding: utf-8 -*-
"""
This file contains conveniences for our slurm development efforts.
"""

import typing
from   typing import *

min_py = (3, 8)

###
# Standard imports.
###

import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

import math
import subprocess

# Credits
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2021'
__credits__ = None
__version__ = str(math.pi**2)[:5]
__maintainer__ = 'George Flanagin'
__email__ = ['me+ur@georgeflanagin.com', 'gflanagin@richmond.edu']
__status__ = 'Teaching example'
__license__ = 'MIT'


def dorunrun(command:Union[str, list],
    timeout:int=None,
    verbose:bool=False,
    quiet:bool=False,
    return_datatype:type=bool
    ) -> tuple:
    """
    A wrapper around (almost) all the complexities of running child 
        processes.
    command -- a string, or a list of strings, that constitute the
        commonsense definition of the command to be attemped. 
    timeout -- generally, we don't
    verbose -- do we want some narrative to stderr?
    quiet -- overrides verbose, shell, etc. 
    return_datatype -- this argument corresponds to the item 
        the caller wants returned.
            bool : True if the subprocess exited with code 0.
            int  : the exit code itself.
            str  : the stdout of the child process.

    returns -- a tuple of values corresponding to the requested info.
    """

    if verbose: sys.stderr.write(f"{command=}\n")

    if isinstance(command, (list, tuple)):
        command = [str(_) for _ in command]
        shell = False

    elif isinstance(command, str):
        shell = True

    else:
        raise Exception(f"Bad argument type to dorunrun: {command}")

    r = None
    try:
        result = subprocess.run(command, 
            timeout=timeout, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            shell=shell)

        code = result.returncode
        if return_datatype is bool:
            return code == 0
        elif return_datatype is int:
            return code
        elif return_datatype is str:
            return result.stdout
        elif return_datatype is tuple:
            return code, result.stdout, result.stderr
        elif return_datatype is dict:
            return {"code":code, "stdout":result.stdout, "stderr":result.stderr}
        else:
            raise Exception(f"Unknown: {return_datatype=}")
        
    except subprocess.TimeoutExpired as e:
        raise Exception(f"Process exceeded time limit at {e.timeout} seconds.")    

    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

