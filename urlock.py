# -*- coding: utf-8 -*-
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
import argparse
from   collections.abc import *
import contextlib
import fcntl
import getpass
import logging

###
# Installed libraries like numpy, pandas, paramiko
###

###
# From hpclib
###
import linuxutils
from   urdecorators import trap
from   urlogger import URLogger

###
# imports and objects that were written for this project.
###

###
# Global objects
###
mynetid = getpass.getuser()
logger = None

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


class URLock:
    """
    Generate an use a lock file as a mutex.
    """

    __slots__    = ('progname', 'dirname', 'lockfilename', 'pid', 'lock_now')
    __values__   = (None, os.getcwd(), None, None, True)
    __defaults__ = dict(zip(__slots__, __values__))

    def __init__(self, **kwargs):
        """
        Use __slots__ to build the object.
        """
        for k, v in URLock.__defaults__.items():
            setattr(self, k, v)
        for k, v in kwargs.items(): 
            if k in URLock.__slots__:
                setattr(self, k, v)
        self.pid = str(os.getpid())

        try:
            self.lockfilename = os.path.join(self.dirname, self.progname) + ".lock"
        except Exception as e:
            raise Exception(f"cannot create a lock file with the supplied name. {e=}")

        ### 
        if self.lock_now: 
            self.lock()


    def __bool__(self) -> bool:
        """
        Return whether the pid in the lock file is our own.
        """
        
        return self.locked_by == self.pid


    def lock(self) -> bool:
        """
        The core of the lock routine.

        returns -- True iff the lock is successful, False otherwise.
        """
        
        ###
        # If the lock file does not exist, then create it and
        # return True.
        ###
        if not os.path.exists(self.lockfilename):
            with open(self.lockfilename, 'wt') as f:
                f.write(self.pid)
            return True

        # Otherwise, is the lock our own?
        return bool(self)


    @property
    def locked_by(self) -> str:
        """
        Return the pid of the locker.
        """
        with open(self.lockfilename) as f:
            return f.read().strip()

                    
    def release(self) -> bool:
        """
        Remove the lock file.
        """
        try:
            os.unlink(self.lockfilename)
            return True
        except FileNotFoundError as e:
            return True
        except Exception as e:
            return False

    unlock = release


@trap
def urlock_main(myargs:argparse.Namespace) -> int:
    global progname

    ###
    # Create an example.
    ###
    locker = URLock(progname=progname)

    ###
    # Create another process, and try to lock. It 
    # should fail.
    ###

    child = os.fork()
    if child:
        child_pid, status, _ = os.wait3(0)

    else:
        child_locker = URLock(progname=progname)
        if child_locker:
            print(f"Oddly the child {child_locker.pid} was able to take over the lock from {child_locker.locked_by}!")
        else:
            print("As expected, the child could not take the lock.")
        os._exit(0)

    if locker:
        print("Locker tests True")
        if locker.release():
            print("Lock was successfully released.")

    else:
        print("Locker tests False")

    # Test the synonym.    
    print(f"{locker.unlock()=}")

    return os.EX_OK


if __name__ == '__main__':

    here       = os.getcwd()
    progname   = os.path.basename(__file__)[:-3]
    configfile = f"{here}/{progname}.toml"
    logfile    = f"{here}/{progname}.log"
    lockfile   = f"{here}/{progname}.lock"
    
    parser = argparse.ArgumentParser(prog="urlock", 
        description="What urlock does, urlock does best.")

    parser.add_argument('--loglevel', type=int, 
        choices=range(logging.FATAL, logging.NOTSET, -10),
        default=logging.DEBUG,
        help=f"Logging level, defaults to {logging.DEBUG}")

    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")
    
    parser.add_argument('-z', '--zap', action='store_true', 
        help="Remove old log file and create a new one.")

    myargs = parser.parse_args()
    logger = URLogger(logfile=logfile, level=myargs.loglevel)

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{progname}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

