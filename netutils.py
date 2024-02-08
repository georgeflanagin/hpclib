# -*- coding: utf-8 -*-
""" Bare functions that support network operations. """

import typing
from   typing import *

import os
import sys


import tempfile

import paramiko

import fileutils
from   sloppytree import SloppyTree

def get_ssh_host_info(host_name:str=None, config_file:str=None) -> List[Dict]:
    """ Utility function to get all the ssh config info, or just that
    for one host.

    host_name -- if given, it should be something that matches an entry
        in the ssh config file that gets parsed.
    config_file -- if not given (as it usually is not) the usual default
        config file is used.
    """

    if config_file is None:
        config_file = fileutils.expandall("~/.ssh/config")
    if not os.path.exists(config_file):
        return [{}]

    ###
    # Paramiko does not process Include directives. Let's create a tempfile
    # from the above, resolve any Include directives, and combine it all into 
    # one file.
    ###
    config_file_lines = open(config_file).readlines()
    the_name = ""
    with tempfile.NamedTemporaryFile(mode='w+t', delete=False) as tf:
        the_name = tf.name
        for line in config_file_lines:
            if line.startswith("Include"):
                fname = fileutils.expandall(line.split()[1])
                if not fname: continue
                included_lines = open(fname).readlines()
                for inc_line in included_lines: 
                    tf.write(inc_line + "\n")
            else:
                tf.write(line + "\n")
        tf.close()

    ssh_conf = paramiko.SSHConfig()
    ssh_conf.parse(open(the_name))

    if not host_name: 
        return ssh_conf
    elif host_name == 'all': 
        return SloppyTree({name:ssh_conf.lookup(name) for name in ssh_conf.get_hostnames()})
    else:
        return ( None if host_name not in ssh_conf.get_hostnames() 
            else SloppyTree(ssh_conf.lookup(host_name)) )



