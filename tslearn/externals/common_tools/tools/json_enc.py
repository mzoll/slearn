'''
Created on Mar 16, 2018

@author: marcel.zoll
'''

import sys
import datetime as dt
import pandas as pd
import numpy as np
import json

import logging
logger = logging.getLogger('JSON_Encoder')

class JSON_Encoder(json.JSONEncoder):
    """ py3 implementation of an extended JSON encoder """
    def default(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (dt.datetime, dt.date)):
            if isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            return obj.isoformat(timespec='microseconds')
        return json.JSONEncoder.default(self, obj)


def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (dt.datetime, dt.date)):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        return obj.isoformat(timespec='microseconds')
    if isinstance(obj, np.float32):
        return float(obj)
    raise TypeError ("Type %s not serializable" % type(obj))


class JSONPacker_ListOfStrings():
    """ packs a list of strings into a JSON object and vise versa;
    truncates the list at front or back to fit an eventual size restriction.
    Has some limited ability to recover
    
    Parameters
    ----------
    max_length : int
        the maximiumn amount of characters reserved for the JSON representation (default: sys.maxsize)
    prioretize_front : bool
        if the native JSO object does not fit the size restriction proretize keeping the head (True) or
        tail of the vector intact (default: True)
     """
    def __init__(self,
                max_length = sys.maxsize,
                prioretize_front =True):
        self.max_length = max_length
        self.prioretize_front = prioretize_front
    def packJSON(self, list_of_strings):
        """ pack a list of strings into a JSON object 
        
        Paramteres
        ----------
        list_of_strings : list of str
            
        Returns
        -------
        str : the JSON string
        """
        if self.max_length <2:
            raise Exception("cannot represent")
            return None
        
        json_obj = json.dumps(list_of_strings)
        if len(json_obj) <= self.max_length:
            return json_obj
        #more treatment, we need to cut from front or back
        if self.prioretize_front:
            i=0
            while i<len(json_obj) and i < self.max_length-1:
                j = i
                i = json_obj.find(',', i+1)
                if i==-1:
                    break
            if j==0:
                return "[]"
            return json_obj[:j]+r']'
        
        else:
            i=0
            while i<len(json_obj) and i <= self.max_length-1:
                j = i
                i = json_obj[::-1].find(',', i+1)
                if i==-1:
                    break
            if j==0:
                return "[]"
            return r'['+json_obj[len(json_obj)-j+1:]
        
    def unpackJSON(self, json_obj, try_recover=True):
        """ Unpack a JSON string object into a list of strings
        
        Parameters
        ----------
        json_obj : str
            the json string object
        try_recover : bool
            Try to recover wrongly truncated lists as list of all valid read elements (default: True)
        """        
        try:
            return json.loads(json_obj)
        except:
            logger.debug('natively JSON unpacking failed: List_of_strings')
            pass  
        
        if try_recover:
            try:
                #find the last comma, cut at this position
                i=0
                while i<len(json_obj):
                    j = i
                    i = json_obj.find(',', i+1)
                    if i==-1:
                        break
                if j==0:
                    return []
                json_obj = json_obj[:j]+r']'
                return json.loads(json_obj)
            except:
                logger.fatal('recovery failed')
        return []
