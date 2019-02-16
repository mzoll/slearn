"""
Created on Feb 17, 2019

@author: marcel.zoll
"""


class _DataPack(object):
    """ collection holding data representing any of the internal classes
    
    Attributes
    ----------
    data : pandas.DataFrame
        holds the row-wise data aligned on index
    header : pandas.DataFrame
        holds the states' header information aligned on index
    meta : pandas.DataFrame
        holds the states' meta information aligned on index
    """

    def __init__(self, header, data, meta):
        self.header = header
        self.data = data
        self.meta = meta

    def startTime(self):
        return self.header['timestamp'].min()

    def endTime(self):
        return self.header['timestamp'].max()

    def copy(self):
        return StatePack(
            self.header.copy(),
            self.data.copy(),
            self.meta.copy())

    def __len__(self):
        return len(self.header)

    def items(self):
        """ get the item representation of the data in this object """
        raise NotImplementedError()

    def append(self, other):
        """ append another object of the same class as this, where the data is the union of both """
        assert(isinstance(other, self.__class__))
        self.header = self.header.append(other.header, ignore_index=True)
        self.header = self.header.reindex()
        self.meta = self.meta.append(other.meta, ignore_index=True)
        self.meta.index = self.header.index
        self.data = self.data.append(other.data, ignore_index=True)
        self.data.index = self.header.index


class IncidentPack(_DataPack):
    def items(self):
        incidents = []
        for i in range(len(self)):
            inc = Incident(
                **self.header.iloc[i].as_dict(),
                data=self.data.iloc[i].as_dict(),
                meta=self.meta.iloc[i].as_dict())
            incidents.append(inc)
        return incidents

class StatePack(_DataPack):
    def items(self):
        states = []
        for i in range(len(self)):
            state = State(
                **self.header.iloc[i].as_dict(),
                meta = self.meta.iloc[i].as_dict())
            state.data.update( self.data.iloc[i].as_dict() )
            states.append(state)
        return states

