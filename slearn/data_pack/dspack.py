"""
Created on Dez 03, 2017

@author: marcel.zoll
"""

import deprecation


@deprecation.deprecated(details="This class will be removed")
class DataStreamPack(object):
    """ collection holding data received from a DW database server (formerly process-data)
    
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
    """

    def __init__(self, data, startTime, endTime, meta={}):
        self.data = data
        self.startTime = startTime
        self.endTime = endTime
        self.meta = meta

    def copy(self):
        return DataStreamPack(self.data.copy(), self.startTime, self.endTime, self.meta.copy())
