'''
Created on Dez 03, 2017

@author: marcel.zoll
'''


class DataStreamPack(object):
    """ collection holding data rerieved from a DW database server (formerly playback-data)
    
    Attributes
    ----------
    meta : dict
        hold meta information to this data
    routingkey : int
        a routing key
    startTime : datetime.datetime
        start of the time-period the data is retrieved for 
    endTime : datetime.datetime
        end of the time-period the data is retrieved for
    data : pandas.DataFrame
        holds the row-wise data
    """
    def __init__(self, routingkey, startTime, endTime, data, meta={}):
        self.routingkey = routingkey
        self.data = data
        self.startTime = startTime
        self.endTime = endTime
        self.meta = meta
    def copy(self):
        return DataStreamPack(self.routingkey, self.startTime, self.endTime, self.data.copy(), self.meta.copy())
    