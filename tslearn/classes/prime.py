'''
Created on Oct 26, 2017

@author: marcel.zoll
'''

from tslearn.classes.state import State

class Prime(object):
    """ collection of preprocessed varibales, logically between the State and model-intern feature extraction  
    
    Parameters
    ----------
    uid : obj
        an unique ID as a global unique identifier of this object and its contents
    targetid : obj 
        an unique ID (typically UserKey) which can be locally clustered, and signals a grouping
    timestamp : datetime.datetime
        timestamp for sequence order
    routingkey : obj
        a key to rout this object through the machinery
    
    Attributes
    ----------
    meta : dict
        meta-information on this object
    data : dict
        holds the data as a flat dictionary
    """
    def __init__(self, uid, targetid, timestamp, routingkey, meta= {}):
        self.uid = uid
        self.targetid = targetid
        self.timestamp = timestamp
        self.routingkey = routingkey
        self.meta = meta
        self.data = {}
    def get(self, key):
        return self.data.get(key)
    def __getitem__(self, key):
        return self.data.get(key)
    @staticmethod
    def fromState(self, state):
        """ just make a one-to-one translation """
        self.uid = state.uid
        self.targetid = state.targetid
        self.timestamp = state.timestamp
        self.routingkey = state.routingkey
        self.data = state.asflatdict()
        self.meta = state.meta
        return self
