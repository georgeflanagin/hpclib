# -*- coding: utf-8 -*-
"""
SloppyTree is derived from Python's dict object. It allows
one to create an n-ary tree of arbitrary complexity whose
members may be accessed by the methods in dict or the object.member
syntax, depending on the usefulness of either expression. 
"""


import typing
from   typing import *

import math
import os
import pprint
import sys


# Credits
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2021'
__credits__ = None
__version__ = str(math.pi**2)[:5]
__maintainer__ = 'George Flanagin'
__email__ = ['me+ur@georgeflanagin.com', 'gflanagin@richmond.edu']
__status__ = 'Teaching example'
__license__ = 'MIT'


class SloppyTree: pass
class SloppyTree(dict):
    """
    Like SloppyDict() only worse -- much worse.
    """

    def __missing__(self, k:str) -> object:
        """
        If we reference an element that doesn't exist, we create it,
        and assign a SloppyTree to its value.
        """
        self[k] = SloppyTree()
        return self[k]


    def __getattr__(self, k:str) -> object:
        """
        Retrieve the element, or implicity call the over-ridden 
        __missing__ method, and make a new one.
        """
        return self[k]


    def __setattr__(self, k:str, v:object) -> None:
        """
        Assign the value as expected.
        """
        self[k] = v


    def __delattr__(self, k:str) -> None:
        """
        Remove it if we can.
        """
        if k in self: del self[k]


    def __ilshift__(self, keys:Union[list, tuple]) -> SloppyTree:
        """
        Create a large number of sibling keys from a list.
        """
        for k in keys:
            self[k] = SloppyTree()
        return self


    def __len__(self) -> int:
        """
        return the number of nodes/branches.
        """
        return sum(1 for _ in (i for i in self.traverse(False)))


    def __invert__(self) -> int: 
        """
        return the number of paths from the root node to the leaves,
        ignoring the nodes along the way.
        """
        return sum(1 for _ in (i for i in self.leaves()))


    def leaves(self) -> object:
        """
        Walk the leaves only, left to right.
        """ 
        for k, v in self.items():
            if isinstance(v, dict):
                yield from v.leaves()
            else:
                yield v


    def __iter__(self) -> object:
        """
        NOTE: dict.__iter__ only sees keys, but SloppyTree.__iter__
        also sees the leaves.
        """
        return self.traverse


    def traverse(self, with_indicator:bool=True) -> Union[Tuple[object, int], object]:
        """
        Emit all the nodes of a tree left-to-right and top-to-bottom.
        The bool is included so that you can know whether you have reached
        a leaf. 

        returns -- a tuple with the value of the node, and 1 => key, and 0 => leaf.

        Usages:
            for node, indicator in mytree.traverse(): ....
            for node in mytree.traverse(with_indicator=False): ....
                ....
        """

        for k, v in self.items():
            yield k, 1 if with_indicator else k
            if isinstance(v, dict):
                yield from v.traverse(with_indicator)
            else:
                yield v, 0 if with_indicator else v

    
    def __str__(self) -> str:
        return self.printable


    @property
    def printable(self) -> str:
        """
        Printing one of these things requires a bit of finesse.
        """
        return pprint.pformat(self, compact=True, indent=4, width=100)


if __name__ == "__main__":
    t = SloppyTree()
    t.a.b.c
    t.a.b.c.d = 6
    t.a.b.d = 5
    t.a['c'].sixteen = "fred"

    for v, indicator in t.traverse():
        print(f"{v}:{indicator}")

    print(f"{t}")
    
