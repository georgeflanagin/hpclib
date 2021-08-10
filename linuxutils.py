# -*- coding: utf-8 -*-
""" Generic, bare functions, not a part of any object or service. """

# Added for Python 3.5+
import typing
from typing import *

import argparse
import atexit
import base64
import binascii
import calendar
import collections
from   collections.abc import Iterable
import contextlib
import copy
from   ctypes import cdll, byref, create_string_buffer
import datetime
import enum
import errno
import fcntl
import fnmatch
import functools
from   functools import reduce
import getpass
import glob
import hashlib
import inspect
import ipaddress
import io
import json
import locale
import operator
import os
import paramiko
import pickle
import pprint as pp
import psutil
import random
import resource
import re
import shlex
import shutil
import signal
import socket
import stat
import string
import subprocess
import sys
import tempfile
import threading
import time
import traceback
try:
    libc = cdll.LoadLibrary('libc.so.6')
except OSError as e:
    print("libc.so.6 has not been loaded.")
    libc = None
    
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

###
# C
###


def columns() -> int:
    """
    If we are in a console window, return the number of columns. 
    Return zero if we cannot figure it out, or the request fails.
    """
    try:
        return int(subprocess.check_output(['tput','cols']).decode('utf-8').strip())
    except:
        return 0


###
# There is no standard way to do this, particularly with virtualization.
###
def cpucounter() -> int:
    names = {
        'macOS': lambda : os.cpu_count(),
        'Linux': lambda : len(os.sched_getaffinity(0)),
        'Windows' : lambda : os.cpu_count()
        }
    return names[platform.platform().split('-')[0]]()


def do_not_run_twice(name:str) -> None:
    """
    Prevents multiple executions at startup. Note that you shouldn't
    call this function from a program after it may have forked into
    multiple processes.
    """
    pids = pids_of(name, True)
    if len(pids):
        tombstone(name + " appears to be already running, and has these PIDs: " + str(pids))
        sys.exit(os.EX_OSERR)


def dorunrun(command:Union[str, list],
    timeout:int=None,
    verbose:bool=False,
    quiet:bool=False,
    return_exit_code:bool=False,
    ) -> Union[bool, int]:
    """
    A wrapper around (almost) all the complexities of running child 
        processes.
    command -- a string, or a list of strings, that constitute the
        commonsense definition of the command to be attemped. 
    timeout -- generally, we don't
    verbose -- do we want some narrative to stderr?
    quiet -- overrides verbose, shell, etc. 
    return_exit_code -- return the actual exit code rather than
        implicitly converting to boolean True for 0.

    returns -- True if the child process returns a zero, or the code.
    """

    if verbose: tombstone(f"{command=}")

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
            shell=shell)

        r = result.returncode

        # Always show errors even if verbose is False.
        if not r:
            verbose and tombstone("Child process terminated without error.")
        elif r < 0:
            tombstone(f"Child process terminated by signal {-r}")
        else:
            verbose and tombstone(f"Child process returned an error: {r}")

        if not quiet:
            if r or shell or verbose:
                tombstone(f"stdout: {result.stdout}")
                tombstone(f"stderr: {result.stderr}")

    except subprocess.TimeoutExpired as e:
        tombstone(f"Process exceeded time limit at {e.timeout} seconds.")    

    except Exception as e:
        tombstone(f"Unexpected error: {str(e)}")
    
    return result.returncode if return_exit_code else (r == 0)


def dump_cmdline(args:argparse.ArgumentParser, return_it:bool=False) -> str:
    """
    Print the command line arguments as they would have been if the user
    had specified every possible one (including optionals and defaults).
    """
    if not return_it: print("")
    opt_string = ""
    for _ in sorted(vars(args).items()):
        opt_string += " --"+ _[0].replace("_","-") + " " + str(_[1])
    if not return_it: print(opt_string + "\n")
    
    return opt_string if return_it else ""


####
# E
####

def explain(code:int) -> str:
    """
    Lookup the os.EX_* codes.
    """
    codes = { _:getattr(os, _) for _ in dir(os) if _.startswith('EX_') }
    names = {v:k for k, v in codes.items()}    
    return names.get(code, 'No explanation for {}'.format(code))


####
# F
####

####
# G
####

def getproctitle() -> str:
    global libc
    try:
        buff = create_string_buffer(128)
        libc.prctl(16, byref(buff), 0, 0, 0)
        return buff.value.decode('utf-8')

    except Exception as e:
        return ""


####
# M
####

def memavail() -> float:
    """
    Return a fraction representing the available memory to run
    new processes.
    """
    with open('/proc/meminfo') as m:
        info = [ _.split() for _ in m.read().split('\n') ]
    return float(info[2][1])/float(info[0][1])


def mymem() -> int:
    info = psutil.Process(os.getpid())
    with info.oneshot():
        return info.memory_full_info().uss


def parse_proc(pid:int) -> dict:
    """
    Parse the proc file for a given PID and return the values
    as a dict with keys set to lower without the "vm" in front,
    and the values converted to ints.
    """
    lines = []
    proc_file = '/proc/'+str(pid)+"/status"
    with open(proc_file, 'r') as f:
        rows = f.read().split("\n")

    if not len(rows): return None

    interesting_keys = ['VmSize', 'VmLck', 'VmHWM', 
            'VmRSS', 'VmData', 'VmStk', 'VmExe', 'VmSwap' ]

    kv = {}
    for row in rows:
        if ":" in row:
            k, v = row.split(":", 1)
        else:
            continue
        if k in interesting_keys: 
            kv[k.lower()[2:]] = int(v.split()[0])

    return kv


def pids_of(process_name:str, anywhere:Any=None) -> list:
    """
    Canøe is likely to have more than one background process running, 
    and we will only know the first bit of the name, i.e., "canoed".
    This function gets a list of matching process IDs.

    process_name -- a text shred containing the bit you want 
        to find.

    anywhere -- unused argument, maintained for backward compatibility.

    returns -- a possibly empty list of ints containing the pids 
        whose names match the text shred.
    """
    results = subprocess.run(['pgrep','-u', 'canoe'], stdout=subprocess.PIPE)
    return [ int(_) for _ in results.stdout.decode('utf-8').split('\n') if _ ]


def setproctitle(s:str) -> str:
    """
    Change the name of the current process, and return the previous
    name for the convenience of setting it back the way it was.
    """
    global libc
    old_name = getproctitle()
    if libc is not None:
        try:
            buff = create_string_buffer(len(s)+1)
            buff.value = s.encode('utf-8')
            libc.prctl(15, byref(buff), 0, 0, 0)

        except Exception as e:
            print(f"Process name not changed: {str(e)}")

    return old_name.encode('utf-8')


def signal_name(i:int) -> str:
    """
    Improve readability of signal processing. 
    """
    try:
        return f"{signal.Signals(i).name} ({signal.strsignal(i)})"
    except:
        return f"unnamed signal {i}"


class SloppyDict: pass
def sloppy(o:object) -> SloppyDict:
    return o if isinstance(o, SloppyDict) else SloppyDict(o)


class SloppyDict(dict):
    """
    Make a dict into an object for notational convenience.
    """
    def __getattr__(self, k:str) -> object:
        if k in self: return self[k]
        raise AttributeError("No element named {}".format(k))

    def __setattr__(self, k:str, v:object) -> None:
        self[k] = v

    def __delattr__(self, k:str) -> None:
        if k in self: del self[k]
        else: raise AttributeError("No element named {}".format(k))

    def reorder(self, some_keys:list=[], self_assign:bool=True) -> SloppyDict:
        new_data = SloppyDict()
        unmoved_keys = sorted(list(self.keys()))

        for k in some_keys:
            try:
                new_data[k] = self[k]
                unmoved_keys.remove(k)
            except KeyError as e:
                pass

        for k in unmoved_keys:
            new_data[k] = self[k]

        if self_assign: 
            self = new_data
            return self
        else:
            return copy.deepcopy(new_data)       


def deepsloppy(o:dict) -> Union[SloppyDict, object]:
    """
    Multi level slop.
    """
    if isinstance(o, dict): 
        o = SloppyDict(o)
        for k, v in o.items():
            o[k] = deepsloppy(v)

    elif isinstance(o, list):
        for i, _ in enumerate(o):
            o[i] = deepsloppy(_)

    else:
        pass

    return o


class SloppyTree(dict):
    """
    Like SloppyDict(), only worse -- much worse.
    """
    def __missing__(self, k:str) -> object:
        self[k] = SloppyTree()
        return self[k]

    def __getattr__(self, k:str) -> object:
        return self[k]

    def __setattr__(self, k:str, v:object) -> None:
        self[k] = v

    def __delattr__(self, k:str) -> None:
        if k in self: del self[k]


def snooze(n:int) -> int:
    """
    Calculate the delay. The formula is arbitrary, and can
    be changed.

    n -- how many times we have tried so far.

    returns -- a number of seconds to delay
    """
    num_retries = 10
    delay = 10
    scaling = 1.2

    if n == num_retries: return None
    nap = delay * scaling ** n
    tombstone('Waiting {} seconds to try again.'.format(nap))
    time.sleep(nap)
    return nap


def squeal(s: str=None, rectus: bool=True, source=None) -> str:
    """ The safety pig will appear when there is trouble. """
    tombstone(str)
    return

    for raster in pig:
        if not rectus:
            print(raster.replace(RED, "").replace(LIGHT_BLUE, "").replace(REVERT, ""))
        else:
            print(raster)

    if s:
        postfix = " from " + source if source else ''
        s = (now_as_string() +
             " Eeeek! It is my job to give you the following urgent message" + postfix + ": \n\n<<< " +
            str(s) + " >>>\n")
    tombstone(s)
    return s


def stalk_and_kill(process_name:str) -> bool:
    """
    This function finds other processes who are named canoed ... and
    kills them by sending them a SIGTERM.

    returns True or False based on whether we assassinated our 
        ancestral impostors. If there are none, we return True because
        in the logical meaning of "we got them all," we did.
    """

    tombstone('Attempting to remove processes beginning with ' + process_name)
    # Assume all will go well.
    got_em = True

    for pid in pids_of(process_name, True):
        
        # Be nice about it.
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            tombstone("Process " + str(pid) + " may have terminated before SIGTERM was sent.")
            continue

        # wait two seconds
        time.sleep(2)
        try:
            # kill 0 will fail if the process is gone
            os.kill(pid, 0) 
        except:
            tombstone("Process " + str(pid) + " has been terminated.")
            continue
        
        # Darn! It's still running. Let's get serious.
        os.kill(pid, signal.SIGKILL)
        time.sleep(2)
        try:
            # As above, kill 0 will fail if the process is gone
            os.kill(pid, 0)
            tombstone("Process " + str(pid) + " has been killed.")
        except:
            continue
        tombstone(str(pid) + " is obdurate, and will not die.")
        got_em = False
    
    return got_em


class Stopwatch:
    """
    Note that the laps are an OrderedDict, so you can name them
    as you like, and they will still be regurgitated in order
    later on.
    """
    conversions = {
        "minutes":(1/60),
        "seconds":1,
        "tenths":10,
        "deci":10,
        "centi":100,
        "hundredths":100,
        "milli":1000,
        "micro":1000000
        }

    def __init__(self, *, units:Any='milli'):
        """
        Build the Stopwatch object, and click the start button. For ease of
        use, you can use the text literals 'seconds', 'tenths', 'hundredths',
        'milli', 'micro', 'deci', 'centi' or any integer as the units. 

        'minutes' is also provided if you think this is going to take a while.

        The default is milliseconds, which makes a certain utilitarian sense.
        """
        try:
            self.units = units if isinstance(units, int) else Stopwatch.conversions[units]
        except:
            self.units = 1000

        self.laps = collections.OrderedDict()
        self.laps['start'] = time.time()    


    def start(self) -> float:
        """
        For convenience, in case you want to print the time when
        you started.

        returns -- the time you began.
        """

        return self.laps['start']


    def lap(self, event:object=None) -> float:
        """
        Click the lap button. If you do not supply a name, then we
        call this event 'start+n", where n is the number of events 
        already recorded including start. 

        returns -- the time you clicked the lap counter.
        """
        if event:
            self.laps[event] = time.time()
        else:
            event = 'start+{}'.format(len(self.laps))
            self.laps[event] = time.time()

        return self.laps[event]
    

    def stop(self) -> float:
        """
        This function is a little different than the others, because
        it is here that we apply the scaling factor, and calc the
        differences between our laps and the start. 

        returns -- the time you declared stop.
        """
        return_value = self.laps['stop'] = time.time()
        diff = self.laps['start']
        for k in self.laps:
            self.laps[k] -= diff
            self.laps[k] *= self.units
            
        return return_value


    def __str__(self) -> str:
        """
        Facilitate printing nicely.

        returns -- a nicely formatted list of events and time
            offsets from the beginning:

        Units are in sec/1000
        ------------------
        start     :  0.000000
        lap one   :  10191.912651
        start+2   :  15940.931320
        last lap  :  27337.829828
        stop      :  31454.867363

        """
        # w is the length of the longest event name.
        w = max(len(k) for k in self.laps)

        # A clever print statement is required.
        s = "{:" + "<{}".format(w) + "}  : {: f}"
        header = "Units are in sec/{}".format(self.units) + "\n" + "-"*(w+20) + "\n"

        return header + "\n".join([ s.format(k, self.laps[k]) for k in self.laps ])


####
# T
####

def this_function():
    """ Takes the place of __function__ in other languages. """

    return inspect.stack()[1][3]


def this_is_the_time(current_minute:int, schedule:list) -> bool:
    """
    returns True if *now* is in the schedule, False otherwise.
    """
    
    t = crontuple_now(current_minute)
    return ((t.minute in schedule[0]) and
            (t.hour in schedule[1]) and
            (t.day in schedule[2]) and
            (t.month in schedule[3]) and
            (t.isoweekday() % 7 in schedule[4]))


def this_line(level: int=1, invert: bool=True) -> int:
    """ returns the line from which this function was called.

    level -- generally, this value is one, meaning that we
    want to use the stack frame that is one-down from where we
    are. In some cases, the value "2" makes sense. Take a look
    at CanoeObject.set_error() for an example.

    invert -- Given that the most common use of this function
    is to generate unique error codes, and that error codes are
    conventionally negative integers, the default is to return
    not thisline, but -(thisline)
    """
    cf = inspect.stack()[level]
    f = cf[0]
    i = inspect.getframeinfo(f)
    return i.lineno if not invert else (0 - i.lineno)


def time_match(t, set_of_times:list) -> bool:
    """
    Determines if the datetime object's parts are all in the corresponding
    sets of minutes, hours, etc.
    """
    return   ((t.minute in set_of_times[0]) and
              (t.hour in set_of_times[1]) and
              (t.day in set_of_times[2]) and
              (t.month in set_of_times[3]) and
              (t.weekday() in set_of_times[4]))


def tombstone(args:Any=None, silent:bool=False) -> Tuple[int, str]:
    """
    Print out a message, data, whatever you pass in, along with
    a timestamp and the PID of the process making the call. 
    Along with printing it out, it returns it.

    if silent, we return the formatted string, but do not print.
    """

    i = str(AX()).rjust(4,'0')
    a = i + " " + now_as_string() + " :: " + str(os.getpid()) + " :: "

    if not silent: sys.stderr.write(a)
    if isinstance(args, str) and not silent:
        sys.stderr.write(args + "\n")
    elif isinstance(args, list) or isinstance(args, dict) and not silent:
        sys.stderr.write("\n")
        for _ in args:
            sys.stderr.write(str(_) + "\n")
        sys.stderr.write("\n")
    else:
        pass
        # p = pp.PrettyPrinter(indent=4, width=512, stream=sys.stderr)
        # p.pprint(formatted_stack_trace())

    if not silent: sys.stderr.flush()

    # Return the info for use by CanoeDB.tombstone()
    return i, a+str(args)
    

std_ignore = [ signal.SIGCHLD, signal.SIGHUP, signal.SIGINT, signal.SIGPIPE, signal.SIGUSR1, signal.SIGUSR2 ]
allow_control_c = [ signal.SIGCHLD, signal.SIGPIPE, signal.SIGUSR1, signal.SIGUSR2 ]
std_die = [ signal.SIGQUIT, signal.SIGABRT ]
def trap_signals(ignore_list:list=std_ignore,
                 die_list:list=std_die):
    """
    There is no particular reason for these operations to be in a function,
    except that if this code moves to Windows it makes sense to isolate
    them so that they may better recieve the attention of an expert.
    """
    global bad_exit
    atexit.register(bad_exit)
    for _ in std_ignore: signal.signal(_, signal.SIG_IGN)
    for _ in std_die: signal.signal(_, bad_exit)

    tombstone("signals hooked.")



def type_and_text(e:Exception) -> str:
    """
    This is not the most effecient code, but by the time this function
    is called, something has gone wrong and performance is unlikely
    to be a relevant point of discussion.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    a = traceback.extract_tb(exc_traceback)
    
    s = []
    s.append("Raised " + str(type(e)) + " :: " + str(e))
    for _ in a:
        s.append(" at file/line " + 
            str(_[0]) + "/" + str(_[1]) + 
            ", in fcn " + str(_[2]))

    return s


####
# U
####

def unwhite(s: str) -> str:
    """ Remove all non-print chars from string. """
    t = []
    for c in s.strip():
        if c in string.printable:
            t.append(c)
    return ''.join(t)


UR_ZERO_DAY = datetime.datetime(1830, 8, 1)
def urdate(dt:datetime.datetime = None) -> int:
    """
    This is something of a pharse. Instead of calculating days from 
    1 Jan 4713 BCE, I decided to create a truly UR calendar starting
    from 1 August 1830 CE. After all, no dates before then could be 
    of any importance to us. 

    Why August? August 1 1830 was a Sunday, so we don't have to do
    anything fancy to get day of the week. For any urdate, urdate%7 
    is the weekday where Sunday is a zero.
    """
    if dt is None: dt = datetime.datetime.today()
    return (dt - UR_ZERO_DAY).days
    

####
# V
####

def valid_item_name(s:str) -> bool:
    """ Determines if s is a valid item name (according to Oracle)

    s -- the string to test. s gets trimmed of white space.
    returns: - True if this is a valid item name, False otherwise.
    """
    return re.match("^[A-Za-z_.]+$", s.strip()) != None


def version(full:bool = True) -> str:
    """
    Do our best to determine the git commit ID ....
    """
    try:
        v = subprocess.check_output(
            ["/opt/rh/rh-git218/root/usr/bin/git", "rev-parse", "--short", "HEAD"],
            universal_newlines=True
            ).strip()
        if not full: return v
    except:
        v = 'unknown'
    else:
        mods = subprocess.check_output(
            ["/opt/rh/rh-git218/root/usr/bin/git", "status", "--short"],
            universal_newlines=True
            ) 
        if mods.strip() != mods: 
            v += (", with these files modified: \n" + str(mods))
    finally:
        return v
        

####
# W
####

def wall(s: str):
    """ Send out a notification on the system. """
    return subprocess.call(['wall "' + s + '"'])

def whoami() -> None:
    """
    Prints the thread id, and the PID of the console you are currently running.

    The purpose of this function is to make it clear which process is sending
    which message in this multi-threaded and multi-processing environment.
    """
    tombstone("Thread id is {} and the PID is {}.".format(threading.get_ident(), os.getpid()))
    tombstone("User is {}, and this CPU is known as {}.".format(me(), socket.gethostname().replace('_','.')))
    tombstone("$CANOE_HOME is {}.".format(os.environ.get('CANOE_HOME', 'not set')))
    tombstone("The git commit ID is {}".format(version()))


