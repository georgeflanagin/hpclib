# -*- coding: utf-8 -*-
"""
Utilities to assist with multiprocessing in Python. Unlike most
of the other modules in HPCLIB that depend only on the decorators
in urdecorators, this module depends on several modules in this
library.
"""
import typing
from   typing import *

###
# Standard imports, starting with os and sys
###
min_py = (3, 8)
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

###
# Other standard distro imports
###
from   collections.abc import *

###
# Installed libraries like numpy, pandas, paramiko
###

###
# From hpclib
###
from   dorunrun import dorunrun
import fileutils
from   sloppytree import SloppyTree
from   urdecorators import trap
from   urlogger import URLogger

###
# Credits
###
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2025, University of Richmond'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = f'gflanagin@richmond.edu'
__status__ = 'in progress'
__license__ = 'MIT'


@trap
def forkssh(list_of_nodes:Iterable, cmd:str, *,
    results_file:Union[str, object]=None,
    no_wait:bool=False,
    logger:URLogger=None,
    user:str='root') -> int:
    '''
    Multiprocesses to ssh to each node and retrieve this information
    in parallel, significantly speeding up the process.

    list_of_nodes  -- hostnames, or just one host name as a str.
    cmd            -- a shell command to execute. The results are assumed
                    to be provided via the remote process's stdout.
    results_file   -- a file or filename to which output may be written
                    as a pickle.
    no_wait        -- if True, do not wait for children to complete. The
                    default is to wait until the last child process
                    completes before moving on.
    logger         -- for errors and debugging.
    user           -- usually, these are done as root.
    '''

    pids = set()
    if isinstance(list_of_nodes, str):
        list_of_nodes = (list_of_nodes,)

    for node in list_of_nodes:

        # Parent process records the child's PID.
        if (pid := os.fork()):
            pids.add(pid)
            logger and logger.debug(f"created child {pid} to handle {node}")
            continue

        # Child executes the argument.

        try:
            cmd = f"""ssh {user}@{node} "{cmd}" """
            result = SloppyTree(dorunrun(cmd, return_datatype=dict))
            if not result.OK:
                logger and logger.error(f'{cmd=} failed on {node=} because {result.name}')
            else:
                results_file and fileutils.append_pickle(result.stdout, results_file)

        finally:
            # ensure the child dies.
            os._exit(os.EX_OK)

    # Back in the parent.
    if no_wait:
        return os.EX_OK

    while pids:
        try:
            child_pid, exit_status, usage = os.wait3(0)
            pids.remove(child_pid)
            logger and logger.info(f"{child_pid} finished with {exit_status=}")
        except KeyboardInterrupt as e:
            logger and logger.error(f"You pressed control-C")

    return os.EX_OK


@trap
def splitter(group:Iterable, num_chunks:int) -> Iterable:
    """
    Generator to divide a collection into num_chunks pieces.
    It works with str, tuple, list, and dict, and the return
    value is of the same type as the first argument.

    group      -- str, tuple, list, or dict.
    num_chunks -- how many pieces you want to have.

    Use:
        for chunk in splitter(group, num_chunks):
            ... do something with chunk ...

    Full test program:

        s = "nowisthewinterofourdiscontent"
        l = list(s)
        t = tuple(s)
        d = dict(zip(s, range(len(s))))

        print([ group for bag in (s, l, t, d) for group in splitter(bag, 5)])
    """

    quotient, remainder = divmod(len(group), num_chunks)
    is_dict = isinstance(group, dict)
    if is_dict:
        group = tuple(kvpair for kvpair in group.items())

    for i in range(num_chunks):
        lower = i*quotient + min(i, remainder)
        upper = (i+1)*quotient + min(i+1, remainder)

        if is_dict:
            yield {k:v for (k,v) in group[lower:upper]}
        else:
            yield group[lower:upper]


