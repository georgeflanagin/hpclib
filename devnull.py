# -*- coding: utf-8 -*-

"""
This is the true null IO object. Every call works, and nothing 
happens. This class solves the problem of returning a "file"
when one is required even if it is impossible to do so.
"""

import os
import random
import base64

# Credits
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2015, University of Richmond'
__credits__ = None
__version__ = '0.1'
__maintainer__ = 'George Flanagin'
__email__ = 'gflanagin@richmond.edu'
__status__ = 'Prototype'

class DevNull: pass
class DevNull:
    """
    DevNull is a file-like object supporting the context
    manager interface commonly used with files. This is a
    rare case where we are keeping the class name in lower
    case to make it look like the common symbol /dev/null.
    """
    # Support for the context manager:
    #
    #     with('myworthlessname') as f:
    #       f.write('something')
    #
    def __init__(self, name:str = None, mode:str='r'):
        self.closed = False
        self.mode = mode
        self.name = name
        pass


    # Implementation details first, other functions follow
    # in alpha order.
    def __bool__(self) -> bool:
        # A real file object returns True.
        return False


    def __enter__(self):
        return self


    def __exit__(self):
        self.closed = True
        pass

    
    def __len__(self) -> int:
        """
        The length of devnull is always zero.
        """
        if self.closed: 
            raise ValueError('I/O operation on closed file.')

        return 0


    def __str__(self) -> str:
        return self.name


    @property
    def readable(self) -> bool:
        return 'r' in self.mode

    @property
    def seekable(self) -> bool:
        return self.mode != 'a'

    @property
    def writeable(self) -> bool:
        return any(_ in self.mode for _ in "aw+")


    # We don't need an open method, but a close is required.
    # open() is a file factory in Python 3.
    def close(self) -> bool:
        """
        Close always succeeds.
        """
        self.closed = True
        return None


    def closed(self) -> bool:
        return self.closed


    def flush(self) -> None:
        pass

    def write(self, datum) -> int:
        """
        return -- the number of chars not written.
        """
        if self.closed: 
            raise ValueError('I/O operation on closed file.')

        try:
            return len(datum)
        except:
            return len(str(datum))


    def read(self, length:int=None) -> str:
        """
        .read is defined to read the entire contents of
        the file. If you give it a length, you get that many
        bytes returned.
        """
        if self.closed: 
            raise ValueError('I/O operation on closed file.')
        if not self.readable:
            raise IOError(f'{self.str} is not open for read.')

        if length is None: return ''
        s = base64.b64encode(os.urandom(length*2))
        if 'b' in self.mode: return s[:length]

        s = s.decode('utf-8')
        return "".join([ _ for _ in s if _.isalpha() ])[:length]


    def readline(self) -> str:
        """
        .readline is defined to read a line of the file, leaving
        the newline at the end.
        """
        if self.closed: 
            raise ValueError('I/O operation on closed file.')

        return self.read(random.randint(40,132))+'\n'


    def seek(self, offset:int, from_where:int=0) -> str:
        """
        We need some reasonable behaviours here. 
        """
        if self.closed: 
            raise ValueError('I/O operation on closed file.')

        if from_where not in [0, 1, 2]: 
            raise ValueError('invalid whence')
        elif from_where == 2 and offset: 
            raise ValueError("can't do nonzero end-relative seeks")
        elif from_where == 1: 
            raise ValueError("can't do nonzero cur-relative seeks")
        elif offset < 0: 
            raise ValueError(f"negative seek position {offset}")
        return offset
        

###
# must_open is just open() that returns a DevNull object
# if the open of the actual file fails.
###
def must_open(name:str, mode:str='r', *args, **kwargs) -> object:
    try:
        return open(name, mode, *args, **kwargs)
    except:
        return DevNull(name, mode)

