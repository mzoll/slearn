'''
Created on Mar 16, 2018

@author: marcel.zoll
'''

import threading
import pickle
import redis

_DEFAULT_REDIS_CRED = {'host': 'localhost', 'port': 6379}

class RedisCache(object):
    """ a radis cache which stores the states as pickled objects """
    def __init__(self, master):
        self.ismaster = False
        self.wait_on_insert = master.wait_on_insert
        self.rpool_params = master.rpool_params
        self.val_ttl = master.val_ttl
    def __del__(self):
        self.teardown()
    def setup(self):
        self.client = redis.client.StrictRedis(**self.rpool_params)
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
            obj = None
        return obj
    def insert(self, routingkey, key, obj):
        cache_key = str(routingkey)+'_'+str(key)
        obj_pickle = pickle.dumps(obj)
        if self.wait_on_insert:
            self.client.setex(name= cache_key, value= obj_pickle, time= self.val_ttl)
        else:        
            threading.Thread(target=self.client.setex, kwargs={'name': cache_key, 'value': obj_pickle, 'time': self.val_ttl}, daemon= False).start()
    def getClient(self):
        return self.__copy__()
    def __copy__(self):
        if not self.ismaster:
            raise Exception('not allowed; already a slave')
        return RedisCache(self)
    def copy(self):
        return self.__copy__()
        
class RedisCache_Master(RedisCache, object):
    """ the master instance of the radis cache interface.
    copies of this object will NOT share the connection, but instantice their own.
    When this master is destroyed it will flush the database, effectivly erazing all data
    
    Parameters
    ----------
    db : int
        an identifier for the database
    rpool_params : dict
        dictionary with keys [host, port] to the redis-server instance
    wait_on_insert : bool
        if True, wait on insert operations to successfully complete before continuing (default: False)
    val_ttl : int >0
        the time to life for each value in seconds
    flush_on_del : bool
        flush the databases when the object is destroyed (default: False)
    """
    def __init__(self, db = 0, rpool_params = _DEFAULT_REDIS_CRED, wait_on_insert=False, val_ttl= 12, flush_on_del=False):
        self.ismaster = True
        self.db = db
        self.wait_on_insert = wait_on_insert
        self.rpool_params = {**rpool_params, 'db': self.db}
        self.val_ttl = val_ttl
        self.client = None
        self.flush_on_del = flush_on_del
    def __del__(self):
        if self.flush_on_del:
            self.client = redis.client.StrictRedis(**self.rpool_params)
            self.client.flushdb()
    

class RedisCache_Pool(object):
    """ an instance that holds a number of connections to a redis-server with different databases.
    inserting and retrieval is an operation which is keyed by the database-number as the routing key
    
    Parameters
    ----------
    rpool_params : dict
        dictionary with keys [host, port] to the redis-server instance
    db : int
        the database to use
    val_ttl : int
        the time to life for each value in seconds; value of 0 disables ttl (default=0)
    wait_on_insert : bool
        if True, wait on insert operations to successfully complete before continuing (default: False)
    flush_on_del : bool
        flush the databases when the object is destroyed (default: False)
    """
    def __init__(self,
            rpool_params = _DEFAULT_REDIS_CRED,
            db = 0,
            val_ttl = 0,
            wait_on_insert= False,
            flush_on_del = False):
        self.rpool_params = rpool_params        
        self.db = db
        self.wait_on_insert = wait_on_insert
        self.val_ttl = val_ttl
        self.flush_on_del = flush_on_del
    def setup(self):
        self.client = redis.client.StrictRedis(**self.rpool_params, db = self.db, socket_keepalive = True)
        return self
    def teardown(self):
        if self.flush_on_del:
            for rediscon in self._rediscon_pool:
                rediscon.flushdb()
        #self.client.close()
        return self
    def insert(self, routingkey, key, obj):
        """ insert a _object_ into the database with _routinkey_ at _key_
        
        Parameters
        ----------
        routingkey : int >= 0
            the integer of the database to store this state to
        state : State obj
            the State object
        """
        cache_key = str(routingkey)+'_'+str(key)
        obj_pickle = pickle.dumps(obj)
        if self.val_ttl:
            if self.wait_on_insert:
                self.client.setex(name= cache_key, value= obj_pickle, time= self.val_ttl)
            else:
                threading.Thread(target=self.client.setex, kwargs={'name': cache_key, 'value': obj_pickle, 'time': self.val_ttl}, daemon= False).start()
        else:
            if self.wait_on_insert:
                self.client.set(name= cache_key, value= obj_pickle)
            else:
                threading.Thread(target=self.client.set, kwargs={'name': cache_key, 'value': obj_pickle}, daemon= False).start()
        
    def fetch(self, routingkey, key):
        """ insert a _object_ into the database _rk_, at the key _state.key_
        
        Parameters
        ----------
        routingkey : int >= 0
            the integer of the database to store this state to
        key : str/int
            the unique identifier, same as _state.key_, for which the state will be retrieved
            
        Returns
        -------
        obj : the object
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
