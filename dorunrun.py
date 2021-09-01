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

import enum
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


class FakingIt(enum.EnumMeta):

    def __contains__(self, something:object) -> bool:
        """
        Normally ... the "in" operator checks if something is in
        an instance of the container. We want to check if a value
        is one of the IntEnum class's members.
        """
        try:
            self(something)
        except ValueError:
            return False

        return True


class ErrorCode(enum.IntEnum, metaclass=FakingIt):
    """
    This is a comprehensive list of exit codes in Linux, and it 
    includes four utility functions. Suppose x is an integer:

        x in ErrorCode    # is x a valid value?
        x.OK              # Workaround: enums all evaluate to True, even if they are zero.
        x.is_signal       # True if the value is a "killed by Linux signal"
        x.signal          # Which signal, or zero.
    """

    @property
    def OK(self) -> bool:
        return self is ErrorCode.EX_OK

    @property
    def is_signal(self) -> bool:
        return ErrorCode.KILLEDBYMAX > self > ErrorCode.EX_KILLEDBYSIGNAL

    @property 
    def signal(self) -> int:
        return self % ErrorCode.EX_KILLEDBYSIGNAL if self.is_signal else 0


    # All was well.
    EX_OK = os.EX_OK

    # It just did not work. No info provided.
    EX_GENERAL = 1

    # BASH builtin error (e.g. basename)
    EX_BUILTIN = 2
    
    # No device or address by that name was found.
    EX_NODEVICE = 6

    # Trying to create a user or group that already exists.
    EX_USERORGROUPEXISTS = 9

    # The execution requires sudo
    EX_NOSUDO = 10

    ######
    # Code 64 is also the usage error, and the least number
    # that has reserved meanings, and nothing above here 
    # should be used by a user program.
    ######
    EX_BASEVALUE = 64
    # command line usage error
    EX_USAGE = os.EX_USAGE
    # data format error
    EX_DATAERR = os.EX_DATAERR
    # cannot open input
    EX_NOINPUT = os.EX_NOINPUT
    # user name unknown
    EX_NOUSER = os.EX_NOUSER
    # host name unknown
    EX_NOHOST = os.EX_NOHOST
    # unavailable service or device
    EX_UNAVAILABLE = os.EX_UNAVAILABLE
    # internal software error
    EX_SOFTWARE = os.EX_SOFTWARE
    # system error
    EX_OSERR = os.EX_OSERR
    # Cannot create an ordinary user file
    EX_OSFILE = os.EX_OSFILE
    # Cannot create a critical file, or it is missing.
    EX_CANTCREAT = os.EX_CANTCREAT
    # input/output error
    EX_IOERR = os.EX_IOERR
    # retry-able error
    EX_TEMPFAIL = os.EX_TEMPFAIL
    # remotely reported error in protocol
    EX_PROTOCOL = os.EX_PROTOCOL
    # permission denied
    EX_NOPERM = os.EX_NOPERM
    # configuration file error
    EX_CONFIG = os.EX_CONFIG

    # The operation was run with a timeout, and it timed out.
    EX_TIMEOUT = 124

    # The request to run with a timeout failed.
    EX_TIMEOUTFAILED = 125

    # Tried to execute a non-executable file.
    EX_NOTEXECUTABLE = 126

    # Command not found (in $PATH)
    EX_NOSUCHCOMMAND = 127

    ###########
    # If $? > 128, then the process was killed by a signal.
    ###########
    EX_KILLEDBYSIGNAL = 128

    # These are common enough to include in the list.
    EX_KILLEDBYCTRLC = 130
    EX_KILLEDBYKILL = 137
    EX_KILLEDBYPIPE = 141
    EX_KILLEDBYTERM = 143

    EX_KILLEDBYMAX = 161

    # Nonsense argument to exit()
    EX_OUTOFRANGE = 255

