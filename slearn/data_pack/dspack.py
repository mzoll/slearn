"""
Created on Dez 03, 2017

@author: marcel.zoll
"""

import warnings
import typing
import datetime as dt

#::: typing
from typing import Dict, Any, Union
NamedDict = Dict['str', Any]


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
    def __init__(self, data, startTime: dt.datetime, endTime: dt.datetime, meta: Union[NamedDict, None] = None):
        self.data = data
        self.startTime = startTime
        self.endTime = endTime
        self.meta = meta if meta is not None else dict()

        warnings.warn("is depricated and will be removed", category=DeprecationWarning,
                      stacklevel=2)

    def copy(self):
        return DataStreamPack(self.data.copy(), self.startTime, self.endTime, self.meta.copy())
