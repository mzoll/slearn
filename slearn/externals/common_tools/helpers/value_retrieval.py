'''
Created on Mar 16, 2018

@author: marcel.zoll
'''

import math
import datetime as dt

def ExpectValue(value,
                default = None, 
                forceType = None):
    """ try to obtain a certain object-type from a provided value, if something goes wrong fall back to a provided default 
    
    Parameters
    ----------
    value : obj
        the passed in value, that will be converted or substituted
    default : obj
        the default that will be returned if inference and coherence will fail; there is no check for type correctness with 'forceType'
        (default: None)
    forceType : str
        string describing the type to be infered on val; if this fails, default will be returned. if None val will only be tested for None
        (default: None)
        
    Returns
    -------
    The checked and converted value
    """
    if value is None:
        return default

    if forceType is None:
        if value is not None:
            return value
        else:
            return default

    # now switch cases if forceType is numeric
    if forceType in ['numeric', 'float', 'double','int','integer', 'posint','positiveinteger']:        
        try:
            if forceType in ['numeric', 'float', 'double']:        
                value = float(value)
            elif forceType in ['int','integer']:
                value = int(value)
            elif forceType in ['posint','positiveinteger']:
                value = abs(int(value))
        except:
            value = default
        finally:
            if math.isnan(value):
                value = default

        return value

    if forceType in ['datetime']:
        if isinstance(value, dt.datetime):
            return value
        else:
            try:
                value = dt.datetime(value)
            except:
                return default 
             
    try:            
        if forceType in ['bool','logical']:
            value = bool(value)
        elif forceType in ['str','string']:
            value = str(value)
        elif forceType == 'char':
            value = str(value)[0]
        else:
            raise Exception("Info : Unable to comprehend forceType to cast to")
        return value
    except:
        return default
    return value


def RetrieveValue(where, varName,
                  default = None, 
                  forceType = None):
    ''' Retrieve variable from a dictionary with type enforcement and fallback

    Parameters
    ----------
    where : dict
        A dictionary that is inspected for the variable
    varName : str
        The name of the value to extract
    default : obj
        A value to default to if the variable did not exist or did not have the correct type and could not be converted
        (default: None)
    forceType : str
        string specifying a type to convert the value to if it doesn't already have that type (default: None)
        
    Returns
    -------
    The value of the specified variable, if it exists and can be handled as the correct type. Otherwise the default value
    '''
    if varName not in where.keys():
        return(default)
  
    value = where[varName]
    # If the result set is a vector or list, no rules apply
    if forceType is None or forceType == 'none':
        return value
    return ExpectValue(value, default=default, forceType=forceType)
