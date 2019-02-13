'''
Created on Dec 8, 2017

@author: marcel.zoll
'''

import multiprocessing
from joblib import Parallel, delayed

def GetNCores(nthreads):
    """ get the number of cores that can be utilized
    
    Parameters
    ----------
    nthreads : int >0
       requested number of cores; 
       if positive number, return min(system_ncores, nthreads)
       if equal to zero, use all cores and return system_ncores
       if negative number, use that many cores less than the maximum and return max(1, ncores+nthreads)
       
    Returns
    -------
    int : number of cores
    """
    ncores = multiprocessing.cpu_count()
    if nthreads == 0 or nthreads is None:
        print('Using all cores : %d' % ncores)
        return ncores
    if nthreads < 0:
        print('Using n cores : %d' % max(1, ncores+nthreads))
        return max(1, ncores+nthreads)
    
    print('Using n cores : %d' % min(ncores, nthreads))
    return min(ncores, nthreads)
