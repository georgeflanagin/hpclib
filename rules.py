# -*- coding: utf-8 -*-
"""
This file contains the data to drive the slurmwriter through the
rules written as navigable branches of the SloppyTree.
"""
import typing
from   typing import *

###
# Standard imports.
###
import os
import os.path
import sys

import datetime
import getpass
import grp
import pwd
import socket
import time
# Putting this import first, we can run pip if we need any of the
# packages named in the try-block.
import slurmutils

import dateparser

###
# Other parts of this project.
###
from   sloppytree import SloppyTree

def NOP(o:object): return o

###
# The netid of the user running this instance of the program.
###

mynetid = getpass.getuser()
VERSION = datetime.datetime.fromtimestamp(os.stat(__file__).st_mtime).isoformat()[:16]

limits = SloppyTree()
limits.ram.leftover = 2
limits.cores.leftover = 2

params = SloppyTree()

###
# These two tuples must be edited for the computer where SLURM is
# being used. There is no obvious way to find the installed software.
###
params.locations.programs = tuple( os.getenv('PATH').split(':') )
params.modulefiles = tuple(slurmutils.all_module_files())
params.programs = {
    'amber':'',
    'bbmap':'',
    'BEAST':'',
    'bedtools':'',
    'bwa':'',
    'cms':'',
    'Columbus':'',
    'gatk':'',
    'gaussian':'',
    'ImageJ':'',
    'mothur':'',
    'NAMD':'',
    'OpenMolcas':'',
    'picard':'',
    'plink':'',
    'qchem':'',
    'qe':'',
    'samtools':'',
    'varscan':'',
    'vcft':''
    }

def program_basename(t:SloppyTree) -> SloppyTree:
    if t.program.answer == "": return t
    for p in params.programs:
        if t.program.answer.startswith(p):
            t.modules = f"module load {p}/{t.program.answer}"
            return t
    return t


def program_launch(t:SloppyTree) -> SloppyTree:
    t.joblines = f"{t.program.answer} {t.inputfile.answer}"
    return t


def program_jobfile(t:SloppyTree) -> SloppyTree:
    global mynetid
    data=t.jobfile.answer
    if not data: return t

    filename=f"/tmp/{mynetid}.recent"
    with open(filename, 'w') as f:
        f.write(t.jobfile.answer)
    return t


def find_software() -> SloppyTree:
    """
    Find the software that is installed on the current machine
    based on the places we know to look. 
    """
    locations = params[socket.gethostname().split('.')[0]].locations
    pass


# If we cannot find the 'sinfo' program, then this is not a SLURM
# machine, or the current user does not have SLURM utilities in
# the PATH.
params.querytool.opts = '-o "%50P %10c  %10m  %25f  %10G %l"'
params.querytool.exe = slurmutils.dorunrun("which sinfo", return_datatype=str).strip()
if not params.querytool.exe:
    sys.stderr.write('SLURM does not appear to be on this machine.')
    sys.exit(os.EX_SOFTWARE)


# Partitions represent where you want to run the program. It is a n-ary tree,
# where the first layer of keys represents the partitions. Subsequent layers
# are tree-nodes with properties of the partition.
partitions = slurmutils.parse_sinfo(params)
all_partitions = set(( k for k in partitions.keys() ))

# This is a list of condos on Spydur. It will not hurt anything to
# leave the code in place, as the set subtraction will have no effect.
condos = set(('bukach', 'diaz', 'erickson', 'johnson', 'parish', 'yang1', 'yang2', 'yangnolin'))
community_partitions_plenum = all_partitions - condos


# programs contains the user-level concepts about the software on this cluster.
programs = SloppyTree()
for p in params.programs:
    programs[p] = None

###
# Each of the trees is a decision tree for the user. Some notes about the
# elements.
#
#  prompt -- if your dialog element has no prompt, the user will not be
#       queried about it. This allows you to put other elements in the tree.
#       Even when these are just strings, they should be lambda functions
#       because the program logic is print(element()) rather than print(element).
#  default -- also a lambda, and if present provides a value when the
#       user fails to type in anything.
#  datatype -- int, str, float, list, etc. Effectively, these are lambda-s
#       because the program coerces the input to this type from str.
#  constraints -- a tuple of lambda-s to check allowable values.
###

dialog = SloppyTree()

dialog.joblines = ""
dialog.modules = ""
dialog.written.foo = lambda : time.strftime(
    '%Y-%m-%d %H:%M:%S', 
    time.localtime(time.time()))

dialog.username.answer = mynetid
dialog.username.groups = slurmutils.mygroups() 
try:
    dialog.username.defaultgroup = [ g for g in dialog.username.groups if "$" in g ][0] 
except:
    dialog.username.defaultgroup = dialog.username.groups[0]

dialog.jobname.prompt = lambda : "Name of your job"
dialog.jobname.datatype = str

dialog.output.prompt = lambda : "Name of your job's output file"
dialog.output.default = lambda : f"{os.getenv('HOME')}/{dialog.jobname.answer}.txt"
dialog.output.datatype = str

dialog.program.prompt = lambda : "What program do you want to run?"
dialog.program.default = lambda : ""
dialog.program.datatype = str
dialog.program.constraints = lambda x : not len(x) or any(x.startswith(y) for y in params.programs),
dialog.program.messages = lambda x : f"""{x} is not a program supported by SlurmWriter. 
    Available programs are {params.programs}""", 
dialog.program.foo = program_basename

dialog.inputfile.prompt = lambda : "Name of your input file"
dialog.inputfile.default = lambda : ""
dialog.inputfile.datatype = str
dialog.inputfile.foo = program_launch

dialog.partition.prompt = lambda : "Name of the partition where you want to run your job?"
dialog.partition.default = lambda : f"{partitions.default_partition}"
dialog.partition.datatype = str
dialog.partition.constraints = lambda x : x in partitions,
dialog.partition.messages = lambda x : f"{x} is not the name of a partition. They are {tuple(x for x in partitions.keys())}.",

dialog.account.prompt = lambda : f"What account is your user id, {mynetid}, associated with?"
dialog.account.default = lambda : f"{dialog.username.defaultgroup}"
dialog.account.datatype = str
dialog.account.constraints = lambda x : x in dialog.username.groups,
dialog.account.messages = lambda x : f"{x} is not one of your groups. They are {dialog.username.groups}",

dialog.datadir.prompt = lambda : "Where is your input data directory?"
dialog.datadir.default = lambda : f"{os.getenv('HOME')}"
dialog.datadir.datatype = str
dialog.datadir.constraints = lambda x : os.path.exists(x), lambda x : os.access(x, os.R_OK)

dialog.scratchdir.prompt = lambda : "Where is your scratch directory?"
dialog.scratchdir.default = lambda : f"/scratch/{dialog.username.answer}"
dialog.scratchdir.datatype = str
dialog.scratchdir.constraints = (
    lambda x: os.makedirs(x, mode=0o750, exist_ok=True) or True, 
    lambda x : os.path.exists(x), 
    lambda x : os.access(x, os.R_OK|os.W_OK) 
    )
dialog.localscratchdir.answer = f"/localscratch/{dialog.username.answer}"

dialog.mem.prompt = lambda : "How much memory (in GB)?"
dialog.mem.default = lambda : 16
dialog.mem.datatype = int
dialog.mem.constraints = lambda x : 1 < x <= partitions[dialog.partition.answer].ram - limits.ram.leftover, 
dialog.mem.messages = lambda x : f"In {dialog.partition.answer}, \
the maximum amount of memory is {partitions[dialog.partition.answer].ram - limits.ram.leftover}",

dialog.cores.prompt = lambda : "How many cores?"
dialog.cores.default = lambda : 8
dialog.cores.datatype = int
dialog.cores.constraints = lambda x : 0 < x <= partitions[dialog.partition.answer].cores - limits.cores.leftover,
dialog.cores.messages = lambda x : f"You may ask for a maximum of {partitions[dialog.partition.answer].cores - limits.cores.leftover} \
cores for jobs in {dialog.partition.answer}.",

dialog.time.prompt = lambda : "How long should this run (in hours)?"
dialog.time.default = lambda : 1
dialog.time.datatype = float
dialog.time.constraints = lambda x : x <= partitions[dialog.partition.answer].max_hours,
dialog.time.reformat = lambda x : slurmutils.hours_to_hms(x)
dialog.time.messages = lambda x : f"The maximum run time is {partitions[dialog.partition.answer].max_hours}.",

dialog.start.prompt = lambda : "When do you want the job to run?"
dialog.start.default = lambda : "now"
dialog.start.datatype = str
dialog.start.constraints = lambda x : x in ('now', 'today', 'tomorrow') or slurmutils.time_check(x),
dialog.start.reformat = lambda x : slurmutils.time_check(x, True)

dialog.jobfile.prompt = lambda : "What will be the name of this new jobfile?"
dialog.jobfile.default = lambda : f"{os.getenv('OLDPWD')}/{dialog.jobname.answer}.slurm"
dialog.jobfile.datatype = str
dialog.jobfile.constraints = lambda x : os.access(os.path.dirname(x), os.W_OK),
dialog.jobfile.messages = lambda x : f"Either {x} doesn't exist, or you cannot write to it.",
dialog.jobfile.foo = program_jobfile

# This is the catch all message if we cannot tell the user something
# more specific.
for k in ( _ for _ in dialog.keys() if 'prompt' in _):
    if 'messages' not in dialog[k]:
        dialog[k].messages = lambda x : f"The value you supplied, {x}, cannot be used here.",

# print(dialog)
# sys.exit(os.EX_OK)
