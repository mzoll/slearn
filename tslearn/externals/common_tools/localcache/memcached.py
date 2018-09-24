'''
Created on Mar 16, 2018

@author: marcel.zoll
'''

import threading
import pickle
import pymemcache
from pymemcache.client.base import Client

_DEFAULT_MEMCACHE_CRED = {'host': 'localhost', 'port': 11211}


class MemcachedCache(object):
    """ a radis cache which stores the states as pickled objects """
    def __init__(self, master):
        self.ismaster = False
        self.wait_on_insert = master.wait_on_insert
        self.memc_params = master.memc_params
        self.val_ttl = master.val_ttl
    def __del__(self):
        self.teardown()
    def setup(self):
        self.client = Client((self.memc_params['host'], self.memc_params['port']), default_noreply= not self.wait_on_insert)
        return self
    def teardown(self):
        return self
    def fetch(self, routingkey, key):
        cache_key = str(routingkey)+'_'+str(key)
        obj_pickle = self.client.get(cache_key)        
        if obj_pickle is None:
            return None
        try:
            obj = pickle.loads(obj_pickle)
        except:
            #logger.debug("Error decoding pickle")
            obj = None
        return obj
    def insert(self, routingkey, key, obj):
        cache_key = str(routingkey)+'_'+key
        obj_pickle = pickle.dumps(obj)
        if self.wait_on_insert:
            self.client.set(key= cache_key, value= obj_pickle, expire= self.val_ttl)
        else:        
            threading.Thread(target=self.client.set, kwargs={'key': cache_key, 'value': obj_pickle, 'expire': self.val_ttl}, daemon= False).start()
    def getClient(self):
        return self.__copy__()
    def __copy__(self):
        if not self.ismaster:
            raise Exception('not allowed; already a slave')
        return MemcachedCache(self)
    def copy(self):
        return self.__copy__()
        
class MemcachedCache_Master(MemcachedCache, object):
    """ the master instance of the memcached cache interface.
    copies of this object will NOT share the connection, but instantice their own.
    When this master is destroyed it can flush the database, effectivly erazing all data
    
    Parameters
    ----------
    memc_params : dict
        dictionary with keys [host, port] to the memcached-server instance
    wait_on_insert : bool
        if True, wait on insert operations to successfully complete before continuing (default: False)
    val_ttl : int >0
        the time to life for each value in seconds
    flush_on_del : bool
        flush the databases when the object is destroyed (default: False)
    """
    def __init__(self, db = 0, memc_params = _DEFAULT_MEMCACHE_CRED, wait_on_insert=False, val_ttl= 12, flush_on_del=False):
        self.ismaster = True
        self.wait_on_insert = wait_on_insert
        self.memc_params = memc_params
        self.val_ttl = val_ttl
        self.flush_on_del= flush_on_del
        self.client = None    
    def __del__(self):
        if self.flush_on_del:
            self.client = Client((self.memc_params['host'], self.memc_params['port']), default_noreply= not self.wait_on_insert)
            self.client.flushdb()
    

class MemcachedCache_Pool(object):
    """ an instance that holds a number of connections to a memcached-server with different databases.
    inserting and retrieval is an operation which is keyed by the database-number as the routing key
    
    Parameters
    ----------
    memc_params : dict
        dictionary with keys [host, port] to the memcached-server instance
    val_ttl : int
        the time to life for each value in seconds; value of 0 disables ttl (default=0)
    wait_on_insert : bool
        if True, wait on insert operations to successfully complete before continuing (default: False)
    flush_on_del : bool
        flush the databases when the object is destroyed (default: False)
    """
    def __init__(self,
            memc_params = _DEFAULT_MEMCACHE_CRED,
            val_ttl = 0,
            wait_on_insert= False,
            flush_on_del = False):
        self.memc_params = memc_params
        self.val_ttl = val_ttl
        self.wait_on_insert = wait_on_insert
        self.flush_on_del = flush_on_del
    def setup(self):
        self.client = Client((self.memc_params['host'], self.memc_params['port']), default_noreply= not self.wait_on_insert)
        return self
    def teardown(self):
        if self.flush_on_del:
            self.client.flush_all(delay=0, noreply=None)
        self.client.close()    
        return self
    def insert(self, routingkey, key, obj):
        """ insert a _state_ into the database _rk_, at the key _state.key_
        
        Parameters
        ----------
        routingkey : int >= 0
            the integer of the database to store this state to
        state : State obj
            the State object
        """
        cache_key = str(routingkey)+'_'+key
        obj_pickle = pickle.dumps(obj) 
        self.client.set(key= cache_key, value= obj_pickle, expire= self.val_ttl)
        
    def fetch(self, routingkey, key):
        """ insert a _state_ into the database _rk_, at the key _state.key_
        
        Parameters
        ----------
        routingkey : int >= 0
            the integer of the database to store this state to
        key : str/int
            the unique identifier, same as _state.key_, for which the state will be retrieved
            
        Returns
        -------
        state : the state
        """
        cache_key = str(routingkey)+'_'+str(key)
        obj_pickle = self.client.get(cache_key)        
        if obj_pickle is None:
            return None
        try:
            obj = pickle.loads(obj_pickle)
        except:
            #logger.debug("Error decoding pickle")
            obj = None
        return obj
