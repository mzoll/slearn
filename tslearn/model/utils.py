"""
Created on Aug 24, 2018

@author: marcel.zoll
"""

from tslearn.externals.common_tools.tools.sort_emit import list_of_uniques, list_of_uniquelistelements, topoSort_gen


def extractUniquePrimeBuilders(primeBuilder_list):
    """ extract the list of unique PrimeBuilders, defined by the uniqueness of their outkeys """
    return list_of_uniquelistelements(primeBuilder_list, lambda e: e.outkeys)


def extractUniqueStateBuilders(primeBuilder_list):
    """ conveninence function: Get the set of unique StateBuilders which are listed in the PrimeBuilder::getStateBuilders() methods """
    stateBuilders = [sb for pb in primeBuilder_list for sb in pb.getStateBuilders()]
    stateBuilders = list_of_uniques(topoSort_gen(stateBuilders, lambda e: e.name, lambda e: e.dep), lambda e: e.name)
    return stateBuilders
