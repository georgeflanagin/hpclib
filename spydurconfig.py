# -*- coding: utf-8 -*-
"""
spydurconfig contains the business rules of the spydur cluster,
i.e., the information that cannot be coded in slurm's rules.
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

###
# Other standard distro imports
###
import argparse
import contextlib
import getpass
mynetid = getpass.getuser()

###
# From hpclib
###
import linuxutils
import setutils
import slurmutils
from   urdecorators import trap

###
# imports and objects that are a part of this project
###
verbose = False

###
# Credits
###
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2022, University of Richmond'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = 'gflanagin@richmond.edu'
__status__ = 'in progress'
__license__ = 'MIT'

config = slurmutils.parse_sinfo()

# If new condos are added, this line will need to reflect the changes.
all_nodes = set(config.keys())
condos = set(('bukach', 'dias', 'erickson', 'johnson', 'parish', 'yang1', 'yang2', 'yangnolin'))
community_nodes = all_nodes - condos

config.bukach.users = set(('cbukach',))
config.dias.users = set(('mdias',))
config.erickson.users = set(('perickso',))
config.johnson.users = setutils.PHI
config.parish.users = set(('cparish', 'dsiriann'))
config.yang1.users = set(('myang',))
config.yang2.users = set(('myang',))
config.yangnolin.users = set(('myang','knolin'))

    
