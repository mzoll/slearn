"""
Created on Dez 03, 2017

@author: marcel.zoll
"""


class DataStreamPack(object):
    """ collection holding data received from a DW database server (formerly playback-data)
    
    Attributes
    ----------
    data : pandas.DataFrame
        holds the row-wise data
    startTime : datetime.datetime
        start of the time-period the data is retrieved for
    endTime : datetime.datetime
        end of the time-period the data is retrieved for
    meta : dict
        hold meta information to this data
    routingkey : int FIXME can this be depricated?
        a routing key
    """

    def __init__(self, routingkey, startTime, endTime, data, meta={}):
        self.routingkey = routingkey
        self.data = data
        self.startTime = startTime
        self.endTime = endTime
        self.meta = meta

    def copy(self):
        return DataStreamPack(self.routingkey, self.startTime, self.endTime, self.data.copy(), self.meta.copy())
