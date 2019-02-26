"""
Created on Oct 26, 2017

@author: marcel.zoll
"""

import copy
import json

from slearn.externals.common_tools.tools.dt_parse import datetime_from_isostring
from slearn.externals.common_tools.tools.json_enc import json_serializer


class State(object):
    """ define a state as a collection of data with mixed persitency
    
    To add information to this object, either use the interface functions 'add' or 'addto', or write to the 
    attributes now, prev, session, total and perm directly
    
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
    data : obj
        a Data object that holds the actual payload
    """

    class _Data():
        """ Proxy class; Holds the data of States as a hierarchical structure of dictionaries with key-value pairs
        
        Attributes
        ----------
        now : dict
            information that is valid only at the current time instant (time, current position etc)
        prev : dict
            information about any previous occurence of a certain event (previous position, previous time, etc)
        session : dict 
            information that is valid only throughout the current session (position sequence, session start time, etc)
        total : dict
            mutable information that is permanently stored (counters, flags, etc)
        perm : dict
            immutable information that is permanently stored (attributes)
        """

        @staticmethod
        def from_dict(d):
            dobj = State._Data()
            for k, v in d.items():
                dobj.__setitem__(k, v)
            return dobj

        def __init__(self):
            self.now = {}
            self.prev = {}
            self.session = {}
            self.total = {}
            self.perm = {}

        @property
        def _props(self):
            return {'now': self.now, 'prev': self.prev, 'session': self.session, 'total': self.total, 'perm': self.perm}

        def to_dict(self):
            return copy.copy(self._props)

        def to_flatdict(self):
            return {'__'.join([n, k]): v for n, p in self._props.items() for k, v in p.items()}

        def __setitem__(self, key, value):
            ks = key.split('__')
            if len(ks) != 2:
                raise ValueError("key '%s' needs to follow the convention '[now,prev,session,total,perm]__key'" % (key))
            if ks[0] in self._props.keys():
                self._props[ks[0]].update({ks[1]: value})

        def set(self, cat, key, value):
            if cat not in self._props.keys():
                raise ValueError("'category not in '[now,prev,session,total,perm]'")
            if len(key.split('__')) > 1:
                raise ValueError("no double-underscore ('__') allowed in key")
            self._props[cat].update({key: value})

        def __getitem__(self, key):
            regkey, valkey = key.split('__')
            if regkey in self._props.keys():
                if valkey in self._props[regkey]:
                    return self._props[regkey][valkey]
            return None

        def get(self, cat, key):
            if cat not in self._props.keys():
                raise ValueError("'category not in '[now,prev,session,total,perm]'")
            if len(key.split('__')) > 1:
                raise ValueError("no double-underscore ('__') allowed in key")
            if cat in self._props.keys():
                if key in self._props[cat].keys():
                    return self._props[cat][key]
            return None

        def update(self, d):
            """ with a bunch of stuff from a dictionary"""
            for k,v in d.items():
                self.__setitem__(k, v)

        def items(self):
            return self.to_flatdict().items()

        def keys(self):
            return ['__'.join([n, k]) for n, p in self._props.items() for n, v in p.items()]

        def copy(self):
            """ make a deep copy """
            return copy.deepcopy(self)

        def clear_now(self):
            """ empty the new part """
            self.now = {}

        def clear_session(self):
            """ empty the session part """
            self.session = {}

        def clear(self):
            """ empty everything """
            self.__init__()

    def __init__(self, uid, targetid, timestamp, meta={}, data={}):
        self.uid = uid
        self.targetid = targetid
        self.timestamp = timestamp
        self.meta = meta
        self.data = self._Data.from_dict(data)

    def __str__(self):
        return f"State(uid:{self.uid}, tid:{self.targetid}, ts:{self.timestamp})::" + \
               "data:{{{}}}".format(list(self.data.keys()))

    def copy(self):
        """ make a deep copy of this object """
        return copy.deepcopy(self)

    def toJSON(self):
        """ dump object to a JSON string """
        json_dict = {}
        json_dict['uid'] = self.uid
        json_dict['targetid'] = self.targetid
        json_dict['timestamp'] = self.timestamp
        json_dict['meta'] = self.meta
        json_dict['data'] = self.data._props
        return json.dumps(json_dict, default=json_serializer)

    @staticmethod
    def fromJSON(json_string):
        """ construct the State from a JSON dump (string) """
        json_dict = json.loads(json_string)
        uid = json_dict['uid']
        targetid = json_dict['targetid']
        timestamp = datetime_from_isostring(json_dict['timestamp'])
        meta_dict = json_dict['meta']
        data_dict = json_dict['data']

        # decode meta information
        for k, v in meta_dict.items():
            if ('Time' in k or 'time' in k) and isinstance(v, str):
                try:
                    meta_dict[k] = datetime_from_isostring(v)
                except:
                    pass

        s = State(uid, targetid, timestamp, meta=meta_dict)

        # decode the data
        for cat, cat_dict in data_dict.items():
            for k, v in cat_dict.items():
                if ('Time' in k or 'time' in k) and isinstance(v, str):
                    try:
                        cat_dict[k] = datetime_from_isostring(v)
                    except:
                        pass
            s.data._props[cat] = cat_dict

        return s
