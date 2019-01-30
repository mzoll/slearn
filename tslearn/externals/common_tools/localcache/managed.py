"""
Created on Jan 31, 2018

@author: marcel.zoll
"""

from multiprocessing import Manager


class ManagedCache(object):
    """ A shared cache through a managed dictionary """

    def __init__(self, managed_dict):
        self.managed_dict = managed_dict

    def setup(self):
        return self

    def teardown(self):
        return self

    def fetch(self, routingkey, key):
        cache_key = str(routingkey) + '_' + str(key)
        return self.managed_dict.get(cache_key)

    def insert(self, routingkey, key, obj):
        cache_key = str(routingkey) + '_' + str(key)
        self.managed_dict[cache_key] = obj

    def get_client(self):
        raise Exception('not allowed; already a slave')

    def __copy__(self):
        raise Exception('not allowed; already a slave')

    def copy(self):
        raise Exception('not allowed; already a slave')


class ManagedCache_Master(ManagedCache, object):
    """ A shared cache through a managed dictionary; 
    observe that this cache cannot evict or expire keys, therefore it is only good for small scale testing
    """

    def __init__(self):
        self.manager = Manager()
        ManagedCache.__init__(self, self.manager.dict())

    def get_client(self):
        return ManagedCache(self.managed_dict)
