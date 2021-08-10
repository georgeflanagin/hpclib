# -*- coding: utf-8 -*-
""" Bare functions that support network operations. """

import typing
from   typing import *

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
        config_file = fileutils.expandall("~") + "/.ssh/config"

    ssh_conf = paramiko.SSHConfig()
    ssh_conf.parse(open(config_file))

    if not host_name: return ssh_conf
    if host_name == 'all': return ssh_conf.get_hostnames()
    return ( None if host_name not in ssh_conf.get_hostnames() 
        else SloppyTree(ssh_conf.lookup(host_name)) )



