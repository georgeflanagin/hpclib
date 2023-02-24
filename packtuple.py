# -*- coding: utf-8 -*-
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
from functools import total_ordering
import getpass
import re
mynetid = getpass.getuser()

###
# From hpclib
###
from dorunrun import dorunrun
import linuxutils
from   urdecorators import trap

###
# imports and objects that are a part of this project
###
verbose = False

###
# Credits
###
__author__ = "Alina Enikeeva" 
__copyright__ = 'Copyright 2022'
__credits__ = None
__version__ = 0.1
__maintainer__ = "ALina Enikeeva"
__email__ = ["alina.enikeeva@richmond.edu"]
__status__ = 'in progress'
__license__ = 'MIT'

class CompareTuple: pass


@trap
def packtuple(packagename: str) -> tuple:
    """
    Breaks down a packagename into parts and converts it into the tuple.
    """

    #some packages have svn12345 as their major. Find them first. If the package name does not contain svn12345, use another pattern
    #38.20130427_r30134.el7.noarch package name does not fit in either of the two packname patterns.
    packname = re.search(r'.*(?=\b\-svn\d+\b)', packagename) 
    if packname == None:
        packname = re.search(r'^[\w+\-]+([^?=\0-9])', packagename)
    
    #print(packagename)
    mmp = re.search(r'\d+\.\d+\.\d+|\d+\.\d+', packagename)  #major, minor and patch all together
    
    datum = re.search(r'\-\w+.*?(\-\d+)', packagename)
    myOS = re.search(r'el\d', packagename)  #####rename the variable!!! use myOS instead
    architecture = re.search(r'\w+$', packagename)
   
    #assign None values to variables that were not matched
    #.group() allows to display an actual string matched, rather than an address of the match
    try:
        packname = packname.group()
    except:
        packname = None

    try:
        mmp = mmp.group().split(".") 
        
        if len(mmp)==3: # all three - major, minor and patch are present in the package name
            major = mmp[0]
            minor = mmp[1]
            patch = mmp[2]
        elif len(mmp)==2: # only major and minor are present
            major = mmp[0]
            minor = mmp[1]
            patch = None

        elif len(mmp)==1: #only major is present
            major = mmp[0]
            minor = None
            patch = None        

    except:
        major = None
        minor = None
        patch = None

    try:
        datum = datum.group(1).split("-")[1] # regex for datum matches two groups. We are interested in group 1, that is 
                                            # why we do .group(1). Regex also matches a dash in front of the datum
                                            # we split on "-" to extract the datum (the number) only

    except:
        datum = None

    try:
        myOS = myOS.group()
    except:
        myOS = None

    try:
        architecture = architecture.group()
    except:
        architecture = None
 
    try: 
        return tuple((packname, major, minor, patch, datum, myOS, architecture,))
    except:
        return "non-standard package name "+ packagename
        


@total_ordering
class CompareTuple:
    """
    This class compares packagenames. 
    """
    def __init__(self, pkgname:str):
        self.packfull = pkgname #full packagename
        self.packtuple = packtuple(pkgname)  
        self.OK = None not in self.packtuple[:3]
    
    def __bool__(self) -> bool:
        """
        Determines if the packagename can be used for comparison.
        Comparison of the packages is possible only for standatd package names.
        Standard package names contain at least name, major and minor.
        """
        return self.OK
 
    def __eq__(self, other:object) -> bool:
        """
        Compares name, major and minor of the packages.
        """ 
        other = CompareTuple(other)
        if self.OK and other.OK: #check if both are instances of a tuple
            return self.getTuple==other.getTuple
    
    def __lt__(self, other:object) -> bool:
        """
        Returns True if the version of the self object is lower than the version of the other object.
        """        
        other = CompareTuple(other)
        if self.OK and other.OK:
            if self.getPackname==other.getPackname:
                return (self.getMajor, self.getMinor) < (other.getMajor, other.getMinor)
        

    def __str__(self) -> str:
        return self.packfull
 
    @property
    def getPackname(self) -> str:
        """
        Returns packagename.
        """
        return self.packtuple[0]
        
    @property
    def getMajor(self) -> str:
        """
        Returns major of the package.
        """
        return self.packtuple[1]        
    
    @property
    def getMinor(self) -> str:
        """
        Returns minor of the package.
        """
        return self.packtuple[2]
 
    @property
    def getTuple(self) -> tuple: 
        """
        Returns tuple for approximate comparison. 
        Tuple contains name, major and minor of the package.
        """        
        return self.getPackname, self.getMajor, self.getMinor

           

@trap
def packtuple_main(myargs:argparse.Namespace) -> int:
    obj = CompareTuple("yelp-3.28.1-1.el7.x86_64")
    obj2 = "yel-3.28.1-2.el7.x86_64"

    print(obj==obj2)
    print(str(obj)) 

    return os.EX_OK


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="packtuple", 
        description="What packtuple does, packtuple does best.")

    parser.add_argument('-i', '--input', type=str, default="",
        help="Input file name.")
    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")
    parser.add_argument('-v', '--verbose', action='store_true',
        help="Be chatty about what is taking place")


    myargs = parser.parse_args()
    verbose = myargs.verbose

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

