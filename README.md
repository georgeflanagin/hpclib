# hpclib

## A list of the primary components.

`beacon` -- a class wrapper around the NIST random number beacon. There is a long
discussion of it here: https://csrc.nist.gov/Projects/interoperable-randomness-beacons/beacon-20

`devnull` -- a class wrapper around a file object that does nothing. 

`dorunrun` -- a function that subprocesses in a consistent way. Also contains an `enum` named
`ExitCode` that names all the Linux exit codes.

`fifo` -- a wrapper around kernel pipes to support interprocess communication.

`fileutils` -- a collection of functions to enhance the use of Python file objects.

`fname` -- a collection of functions as class members of an `Fname` object that manipulate the information about files
from their the directory entries. 

`linuxutils` -- a collection of functions that provide interfaces to common
(and uncommon) interactions with the Linux OS.

`netutils` -- a small collection of network conveniences.

`parsec4` -- a parser toolkit based on parsec3 by He Tao, which was in turn
derived from Haskell's parsec library.

`setutils` -- extended operations on sets, along with the global definitions of 
PHI (empty set) and the Universal set.

`sloppytree` -- a tree for Python. Also includes a SloppyDict and functions to convert
built-in Python types to the new, slop.py types.

`slurmutils` -- functions for accessing SLURM's info from Python.

`sqlitedb` -- a class that represents a database connection to SQLite3. Supports locking.

`urdecorators` -- really, there is only one, `@trap`. It creates a nicely formatted dump
of all local and global symbols at the time a Exception is raised.

`urlogger` -- a simple wrapper around the functions in Python's built-in `logging`.

`urpacker` -- a wrapper around the Burrows-Wheeler transform to efficiently compress
data. You can read more about it here: https://en.wikipedia.org/wiki/Burrows–Wheeler_transform
