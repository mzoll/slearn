'''
Created on Aug 17, 2018

@author: marcel.zoll
'''

def reform_incidentId(dataStreamPack, timefield_name):
    """ sort the dataframe in increasing time-order and reset the row index to a incremental value.
    
    NOTE: this is an incplace operation """
    dataStreamPack.data.sort_values(timefield_name, inplace=True)
    dataStreamPack.data.index = list(range(len(dataStreamPack.data)))
    return dataStreamPack
    