"""
Created on Jan 22, 2018

@author: marcel.zoll
"""


class Result(object):
    """ define a result as the output of a computation by a single or lineup of multiple scoring-algorithms
    
    Parameters
    ----------
    uid : obj
        an unique ID as a global unique identifier of this object and its contents
    targetid : obj 
        an unique ID (typically UserKey) which can be locally clustered, and signals a grouping
    timestamp : datetime.datetime
        timestamp for sequence order

    Attributes
    ----------
    meta : dict
        meta-information on this object
    data : dict
        holds the result information 
    """
    def __init__(self, uid, targetid, timestamp, routingkey=None, meta={}):
        self.uid = uid
        self.targetid = targetid
        self.timestamp = timestamp
        self.meta = meta
        self.data = {}
