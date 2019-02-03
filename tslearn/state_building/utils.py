"""
Created on Aug 24, 2018

@author: marcel.zoll
"""

from tslearn.externals.common_tools.tools.sort_emit import list_of_uniques, topoSort_gen

def extractUniqueStateBuilders(stateBuilder_list):
    """ conveninence function: Get the set of unique StateBuilders """
    return list_of_uniques(topoSort_gen(stateBuilder_list, lambda e: e.name, lambda e: e.dep), lambda e: e.name)
