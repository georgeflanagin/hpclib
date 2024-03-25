#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is a base class for manipulating all sqlite databases.
"""


#pragma pylint=off
    
# Credits
__author__ =        'George Flanagin'
__copyright__ =     'Copyright 2017 George Flanagin'
__credits__ =       'None. This idea has been around forever.'
__version__ =       '1.0'
__maintainer__ =    'George Flanagin'
__email__ =         'me+git@georgeflanagin.com'
__status__ =        'continual development.'
__license__ =       'MIT'

import typing
from   typing import *

import inspect
import os
import multiprocessing
import sqlite3
import sys
import tempfile
import time

try:
    import pandas
    we_have_pandas = True
except Exception as e:
    we_have_pandas = False

from dorunrun import dorunrun
from urdecorators import *

class SQLiteDB:
    """
    Basic functions for manipulating all sqlite3 databases. The first
    argument is positional, and is the name of the database to be
    opened. All other arguments are keyword-style. Here is a summary of
    the keyword options:

        isolation_level -- one of EXCLUSIVE, DEFERRED, IMMEDIATE as defined
            in the documentation at sqlite.org. (default:DEFERRED)

        lock -- A multiprocessing.RLock object created elsewhere, and to
            be used as the database semaphore. If this argument is not
            supplied, or is explicitly None, then a new multiprocessing.RLock
            object is created.

        to_RAM -- if True, the entire database is read into RAM on open,
            and the close() operation will write it back to wherever it
            came from. (default:False)

        timeout -- a number of seconds to wait for anything that is 
            waitable. A connection, a commit, etc. (default:15)

        use_pandas -- if True, and pandas is installed, the results of 
            all SELECT operations will be returned in a pandas.DataFrame.
            (default:True)

    And these are the class members:

        cursor -- The sqlite3.cursor object.

        db -- The object that is a handle to the SQLite3 database.

        OK -- Boolean set to true if the most recent operation succeeded.

        stmt -- The most recently executed (or attempted) SQL statement. 

    """
    _instance = None

    __slots__ = ( 'stmt', 'OK', 'db', 'cursor', 
        'timeout', 'isolation_level', 'name', 'use_pandas', 'to_RAM', 'lock' )
    __values__ = ( '', False, None, None,
        15, 'DEFERRED', '', True, False, multiprocessing.RLock() )
    __defaults__ = dict(zip(
        __slots__, __values__
        ))

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None: return cls._instance

        if os.path.exists(args[0]):
            cls._instance = SQLiteDB.__init__(args[0], **kwargs)
        return cls._instance


    def __init__(self, path_to_db:str, **kwargs):

        # Set the defaults.
        for k, v in SQLiteDB.__defaults__.items():
            setattr(self, k, v)

        # Override the defaults if the keywords appear in the call.
        for k, v in kwargs.items(): 
            if k in SQLiteDB.__slots__:
                setattr(self, k, v)

        error_on_init = True
        try:
            self.db = sqlite3.connect(self.name, 
                timeout=self.timeout, isolation_level=self.isolation_level)

            if self.to_RAM:
                memDB = sqlite3.connect(':memory:')
                self.db.backup(memDB, pages=0, progress=None)
                self.db.close()
                self.db = memDB
                
            self.cursor = self.db.cursor()
            self.keys_on()
            error_on_init = False

        except sqlite3.OperationalError as e:
            sys.stderr.write(str(e))
            
        finally:
            self.OK = not error_on_init


    def __str__(self) -> str:
        """ For simplicity """

        return self.name


    def __bool__(self) -> bool:
        """
        We consider everything "OK" if the object is attached to an open 
        database, and the last operation went well.
        """
        return self.db is not None and self.OK


    def __call__(self) -> sqlite3.Cursor:
        """
        This is a bit of syntax sugar to get the cursor object
        out from inside the object. The purpose is to use it
        with the pandas library.
        """

        if not self.db: raise Exception('Not connected!')
        return self.db


    @property
    def num_connections(self) -> int:
        """
        Determine the number of open connections to this database.

        NOTE: this function will work if the self.name object is valid
            even if this process does not have the database currently
            open.

        returns:
            -1 : if the name is invalid.
             0 : if the database is not open at all.
             n : the number of open connections.
        """
        if not self.name: return -1
        if not os.path.exists(self.name): return -1

        return max(len(dorunrun(f"lsof {self.name}", return_datatype=str).split()) - 1, 0)
        
    
    def __len__(self) -> int:
        """
        Syntax sugar to allow a reference to the number of
        connections as len(db), where db is an object of type
        SQLiteDB.
        """
        return self.num_connections


    def keys_off(self) -> None:
        self.cursor.execute('pragma foreign_keys = 0')
        self.cursor.execute('pragma synchronous = OFF')


    def keys_on(self) -> None:
        self.cursor.execute('pragma foreign_keys = 1')
        self.cursor.execute('pragma synchronous = FULL')


    @trap
    def close(self) -> bool:
        """
        close the database, carefully copying a memory
        resident database to disc. 
        """

        # Commit any pending transactions.
        self.commit()

        # First, check to see if other processes have the
        # the database open.
        if self.num_connections > 1: return True

        ###
        # If there is nothing to copy back, then the actions
        # a clear
        if not self.to_RAM:
            # Forgive the error where close() is called twice.
            if not self.db: return False
            # Mark the object as closed.
            self.OK = False
            # Let the caller know if it worked.
            return self.db.close()

        # Let's not overwrite the existing DB until
        # we have saved the in-memory data.
        db_dir, _ = os.path.split(self.name)
        temp_db_name = os.path.join(db_dir,
            next(tempfile._get_candidate_names()))

        try:
            # Create a new DB that is empty, and run backup
            # to it.
            temp_db = sqlite3.connect(temp_db_name)
            self.db.backup(temp_db, pages=0, progress=None)

            # Delete the original database.
            os.unlink(self.name)
            # Create a link to it.
            os.link(temp_db_name, self.name)

        except Exception as e:
            print(f"Exception raised saving in-memory database.\n{e=}")  
            raise

        else:   
            return True

        finally:
            self.OK = False
            self.db.close()
            os.unlink(temp_db_name)


    @trap
    def commit(self) -> bool:
        """
        Expose this function so that it can be called without having
        to put the dot-notation in the calling code.
        """
        try:
            with self.lock:
                self.db.commit()
            return True

        except:
            return False


    @trap
    def execute_SQL(self, SQL:str, *args, **kwargs) -> object:
        """
        Wrapper that automagically returns rowsets for SELECTs and 
        number of rows affected for other DML statements.
        
        is_select        -- if we think it is a SELECT statement.
        has_args         -- to avoid the problem with the None-tuple.
        self.use_pandas  -- iff True, return a DataFrame on SELECT statements.

        """ 
        global we_have_pandas
       
        docommit = kwargs.get('transaction') is None
        is_select = SQL.strip().lower().startswith('select')
        has_args = not not args

        if we_have_pandas and self.use_pandas and is_select:
            return pandas.read_sql_query(SQL, self.db, *args)
        
        if has_args:
            rval = self.cursor.execute(SQL, args)
        else:
            rval = self.cursor.execute(SQL)

        if is_select: return rval.fetchall()
        docommit and self.commit()
        return rval


    def row_one(self, SQL:str, parameters:Union[tuple, None]=None) -> dict:
        """
        Return only the first row of the results. When returned,
        it will not be a list with one row, but just the row 
        itself. If the column is provided, then only that column
        is returned as an atomic datum.
        """
       
        results = self.execute_SQL(SQL, parameters)
        return None if not results else results[0]


