# -*- coding: utf-8 -*-
""" Generic, bare functions, not a part of any object or service. """

# Added for Python 3.5+
import typing
from typing import *

import argparse
import atexit
import collections
from   collections.abc import Iterable
import copy
from   ctypes import cdll, byref, create_string_buffer
import datetime
import dateutil
from   dateutil import parser
import enum
import glob
import grp
import inspect
import os
import platform
import pwd
import re
import signal
import socket
import string
import subprocess
import sys
import threading
import time
import traceback
try:
    libc = cdll.LoadLibrary('libc.so.6')
except OSError as e:
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
# B
###
def bookmark() -> list:
    """
    Return a list of function calls that arrived at this
    one. If no information is available, return an empty
    list.

    bookmark()'s list does not include itself, therefore the
    range() statement starts at 1 rather than zero. Note that
    if you are printing the list, you probably don't care
    about the print() function, so you should 

    print(bookmark()[1:])
    """
        
    stak = inspect.stack()
    return [ stak[i].function 
        for i in range(1, len(stak)) 
        if stak[i].function not in ('wrapper', '<module>', '__call__') ]
        

byte_remap = {
    'PB':'P',
    'TB':'T',
    'GB':'G',
    'MB':'M',
    'KB':'K'
    }


byte_scaling = {
    'P':1024**5,
    'T':1024**4,
    'G':1024**3,
    'M':1024**2,
    'K':1024**1,
    'B':1024**0,
    'X':None
    }


def byte_scale(i:int, key:str='X') -> str:
    """
    i -- an integer to scale.
    key -- a character to use for scaling.
    """
    try:
        divisor = byte_scaling[key]
    except:
        return ""

    try:
        return f"{round(i/divisor, 3)}{key}"
    except:
        for k, v in byte_scaling.items():
            if i > v: return f"{round(i/v, 3)}{k}"
        else:
            # How did this happen?
            return f"Error: byte_scale({i}, {k})"

def bytes2human(n:int) -> str:
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def byte_size(s:str) -> int:
    """
    Takes a string like '20K' and changes it to 20*1024.
    Note that it accepts '20k' or '20K'
    """ 
    if not s: return 0

    # Take care of the case where it is KB rather than K, etc.
    if s[-2:] in byte_remap:
        s = s[:-2] + byte_remap[s[-2:]]

    try:
        multiplier = byte_scaling[s[-1].upper()]
        the_rest = int(s[:-1])
        return the_rest*multiplier
    except:
        return 0


###
# C
###

def coerce(s:str) -> Union[int, float, datetime.datetime, tuple, str]:
    """
    Examine a shred of str data, and see if we can make something 
    more structured from it. 
    """
    try:
        return int(s)
    except:
        pass

    try:
        return float(s)
    except:
        pass

    try:
        return parser.parse(s)
    except:
        pass

    if ',' in s:
        try:
            return tuple(coerce(part) for part in s.split(','))
        except:
            pass

    return s
        

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


###
# D
###

def daemonize_me() -> bool:
    """
    Turn this program into a daemon, if it is not already one.
    """
    if os.getppid() == 1: return

    try:
        pid = os.fork()
        if pid: sys.exit(os.EX_OK)

    except OSError as e:
        print(f"Fork failed. {e.error} = {e.strerror}")
        sys.exit(os.EX_OSERR)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid:
            print(f"Daemon's PID is {pid}")
            sys.exit(os.EX_OK)

    except OSError as e:
        print(f"Second fork failed. {e.error} = {e.strerror}")
        sys.exit(os.EX_OSERR)

    else:
        return True


def dump_cmdline(args:argparse.ArgumentParser, return_it:bool=False, split_it:bool=False) -> str:
    """
    Print the command line arguments as they would have been if the user
    had specified every possible one (including optionals and defaults).
    """
    if not return_it: print("")
    opt_string = ""
    sep='\n' if split_it else ' '
    for _ in sorted(vars(args).items()):
        opt_string += f"{sep}--"+ _[0].replace("_","-") + " " + str(_[1])
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
def getallgroups():
    """
    We only care about the ones over 2000.
    """
    yield from ( _.gr_name for _ in grp.getgrall() if _.gr_gid > 2000 )


def getgroups(u:str) -> tuple:
    """
    Return a tuple of all the groups that "u" belongs to.
    """
    groups = [g.gr_name for g in grp.getgrall() if u in g.gr_mem]
    try:
        primary_group = pwd.getpwnam(u).pw_gid
    except KeyError as e:
        return tuple()

    groups.append(grp.getgrgid(primary_group).gr_name)
    return tuple(groups)


def getproctitle() -> str:
    global libc
    try:
        buff = create_string_buffer(128)
        libc.prctl(16, byref(buff), 0, 0, 0)
        return buff.value.decode('utf-8')

    except Exception as e:
        return ""


default_group = 'people'
def getusers_in_group(g:str) -> tuple:
    """
    Linux's group registry does not know about the default group
    that is kept in LDAP. 
    TODO: This function requires some cleanup before release.
    """

    global default_group
    try:
        return ( tuple(",".join(glob.glob('/home/*')).replace('/home/','').split(','))
            if g == default_group else
            tuple(grp.getgrnam(g).gr_mem) )
    except KeyError as e:
        return tuple()


def group_exists(g:str) -> bool:
    try:
        grp.getgrnam(g)
        return True
    except KeyError as e:
        return False    

####
# H
####

def hms_to_hours(hms:str) -> float:
    """
    Convert a slurm time like 2-12:00:00 to
    a number of hours.
    """

    try:
        h, m, s = hms.split(':')
    except Exception as e:
        if hms == 'infinite': return 365*24
        return 0

    try:
        d, h = h.split('-')
    except Exception as e:
        d = 0

    return int(d)*24 + int(h) + int(m)/60 + int(s)/3600


def hours_to_hms(h:float) -> str:
    """
    Convert a number of hours to "SLURM time."
    """

    days = int(h / 24)
    h -= days * 24
    hours = int(h)
    h -= hours
    minutes = int(h * 60)
    h -= minutes/60
    seconds = int(h*60)

    return ( f"{hours:02}:{minutes:02}:{seconds:02}"
        if h < 24 else
        f"{days}-{hours:02}:{minutes:02}:{seconds:02}" )



####
# I
####
def is_faculty(netid:str) -> bool:
    try:
        return is_valid_netid(netid) and not netid[2] in string.digits
    except Exception as e:
        return False


def is_student(netid:str) -> bool:
    return True
    try: 
        return is_valid_netid(netid) and netid[2] in string.digits
    except Exception as e:
        return False


def is_valid_netid(netid:str) -> bool:
    try:
        return len(getgroups(netid))!=0
    except Exception as e:
            return False


def iso_time(seconds:int) -> str:
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seconds))


def iso_seconds(timestring:str) -> int:
    dt = datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M')
    return dt.strftime("%s")

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


def mygroups() -> Tuple[str]:
    """
    Collect the group information for the current user, including
    the self associated group, if any.
    """
    return getgroups(getpass.getuser())


####
# N
####

def now_as_seconds() -> int:
    return time.clock_gettime(0)


def now_as_string(replacement:str=' ') -> str:
    """ Return full timestamp for printing. """
    return datetime.datetime.now().isoformat()[:21].replace('T',replacement)


####
# P
####

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


####
# S
####

def script_driven() -> bool:
    """
    returns True if the input is piped or coming from an IO redirect.
    """

    mode = os.fstat(0).st_mode
    return True if stat.S_ISFIFO(mode) or stat.S_ISREG(mode) else False


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


def time_print(s:str) -> None:
    sys.stderr.write(f"{now_as_string()} :: {s}\n")


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


def tombstone(args:Any=None, silent:bool=False) -> str:
    """
    Print out a message, data, whatever you pass in, along with
    a timestamp and the PID of the process making the call. 
    Along with printing it out, it returns it.

    if silent, we return the formatted string, but do not print.
    """

    a = " " + now_as_string() + " :: " + str(os.getpid()) + " :: "

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

    if not silent: sys.stderr.flush()

    # Return the info for use by CanoeDB.tombstone()
    return a+str(args)
    

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


def user_from_uid(uid:int) -> str:
    return dorunrun("id -nu {uid}", return_datatype=str)


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
            ["git", "rev-parse", "--short", "HEAD"],
            universal_newlines=True
            ).strip()
        if not full: return v
    except:
        v = 'unknown'
    else:
        mods = subprocess.check_output(
            ["git", "status", "--short"],
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


def whereami() -> str:
    """
    Primarily to determine if the program is running on the cluster
    or the webserver, but this function can also return other info.
    """
    hostname = socket.gethostname()
    if hostname == 'spdrweb.richmond.edu': return 'webserver'
    if hostname == 'spydur.cluster': return 'headnode'
    if '.cluster' in hostname: return 'computenode'
    if '.richmond.edu' in hostname: return 'oncampus'
    return 'offcampus'
    


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


